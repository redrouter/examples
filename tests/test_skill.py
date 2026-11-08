import contextlib
import importlib.util
import io
import json
import os
import re
import socket
import unittest
from http.client import IncompleteRead
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/redrouter"
spec = importlib.util.spec_from_file_location("request", SKILL / "scripts/request.py")
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)


class NoNetwork(unittest.TestCase):
    def setUp(self):
        self.network = patch.object(
            socket.socket, "connect", side_effect=AssertionError("Network forbidden in tests")
        )
        self.network.start()
        self.addCleanup(self.network.stop)

    def run_cli(self, args, env=None):
        out, err = io.StringIO(), io.StringIO()
        with (
            patch.dict(os.environ, env or {}, clear=True),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(err),
        ):
            code = rr.main(args)
        return code, out.getvalue(), err.getvalue()


class SkillStructure(NoNetwork):
    def test_standard_frontmatter_and_one_discoverable_skill(self):
        skills = list((ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(skills, [SKILL / "SKILL.md"])
        content = skills[0].read_text()
        self.assertTrue(content.startswith("---\n"))
        _, header, body = content.split("---", 2)
        metadata = yaml.safe_load(header)
        self.assertLessEqual(
            set(metadata),
            {"name", "description", "license", "compatibility", "metadata", "allowed-tools"},
        )
        name = metadata["name"]
        self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertEqual(name, SKILL.name)
        self.assertTrue(1 <= len(metadata["description"]) <= 1024)
        if "compatibility" in metadata:
            self.assertTrue(1 <= len(metadata["compatibility"]) <= 500)
        self.assertTrue(
            all(isinstance(k, str) and isinstance(v, str) for k, v in metadata["metadata"].items())
        )
        self.assertTrue(body.strip())
        self.assertLess(len(body.splitlines()), 200)

    def test_relative_links_are_bundled_and_resolve(self):
        for document in [ROOT / "README.md", *SKILL.rglob("*.md"), *(ROOT / "docs").glob("*.md")]:
            if ".venv" in document.parts:
                continue
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text()):
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                    continue
                resolved = (document.parent / target.split("#")[0]).resolve()
                self.assertTrue(resolved.is_relative_to(ROOT), target)
                self.assertTrue(resolved.is_file(), target)
                if document == SKILL / "SKILL.md":
                    self.assertTrue(resolved.is_relative_to(SKILL), target)

    def test_no_local_identity_paths_or_secret_files(self):
        for directory in [SKILL, ROOT / "docs", ROOT / "scripts", ROOT / "tests"]:
            for path in directory.rglob("*"):
                self.assertFalse(path.is_symlink(), path)
                if path.is_file() and path.suffix in {".md", ".py"}:
                    self.assertNotIn("/" + "Users" + "/", path.read_text())
                self.assertNotIn(path.name, {".env", "id_rsa", "id_ed25519"})


class Examples(NoNetwork):
    def test_default_examples_never_read_key_or_open_network(self):
        original_get = os.environ.get

        def guarded_get(name, *args):
            self.assertNotEqual(name, "REDROUTER_API_KEY")
            return original_get(name, *args)

        with (
            patch.object(os.environ, "get", side_effect=guarded_get),
            patch.object(rr, "fetch_json") as network,
        ):
            for interface in rr.PATHS:
                for security in (False, True):
                    args = ["--interface", interface] + (["--security"] if security else [])
                    code, out, err = self.run_cli(args)
                    self.assertEqual(code, 0)
                    self.assertIn("MOCK ONLY", out)
                    self.assertIn("no API key read", err)
            network.assert_not_called()

    def test_live_approval_flags_must_be_paired_before_network_or_key_access(self):
        for flag in ("--live", "--approve-api-use"):
            with (
                patch.object(rr, "fetch_json") as network,
                contextlib.redirect_stderr(io.StringIO()),
            ):
                with self.assertRaises(SystemExit) as error:
                    rr.main([flag])
                self.assertEqual(error.exception.code, 2)
                network.assert_not_called()

    def test_wire_payload_shapes(self):
        for interface in rr.PATHS:
            body = rr.make_payload(interface, "selected-model")
            self.assertEqual(body["model"], "selected-model")
            self.assertNotIn("stream", body)
            if interface == "responses":
                self.assertEqual(body["max_output_tokens"], 512)
                self.assertIs(body["store"], False)
                self.assertIsInstance(body["input"], str)
                self.assertNotIn("max_tokens", body)
            else:
                self.assertEqual(body["max_tokens"], 512)
                self.assertEqual(body["messages"][0]["role"], "user")
                self.assertNotIn("max_output_tokens", body)

    def test_security_payload_contains_only_the_bundled_sample(self):
        sample = (SKILL / "assets/sanitized_sample.py").read_text()
        for interface in rr.PATHS:
            body = rr.make_payload(interface, rr.DEFAULT_MODEL, True)
            prompt = body.get("input") or body["messages"][0]["content"]
            self.assertIn(sample, prompt)
            self.assertIn("Do not execute anything", prompt)
            self.assertIn("local regression tests", prompt)
            self.assertEqual(body.get("max_tokens", body.get("max_output_tokens")), 2048)
            self.assertNotIn("tools", body)
        compile(sample, "sanitized_sample.py", "exec")  # Syntax check, never execute.

    def test_complete_and_incomplete_responses(self):
        for interface in rr.PATHS:
            body = rr.mock_response(interface)
            self.assertIn("MOCK ONLY", rr.extract_text(interface, body))
            if interface == "chat":
                body["choices"][0]["finish_reason"] = "length"
            elif interface == "messages":
                body["stop_reason"] = "max_tokens"
            else:
                body["status"] = "incomplete"
            with self.assertRaises(rr.RequestFailure):
                rr.extract_text(interface, body)
            with self.assertRaises(rr.RequestFailure):
                rr.extract_text(interface, {})

    def test_responses_parser_skips_reasoning_items(self):
        body = rr.mock_response("responses")
        body["output"].insert(0, {"type": "reasoning", "summary": []})
        self.assertIn("MOCK ONLY", rr.extract_text("responses", body))

    def test_model_availability_and_output_limit_checked_before_credential_dispatch(self):
        for models in (
            [],
            [{"id": rr.DEFAULT_MODEL, "available": False}],
            [{"id": rr.DEFAULT_MODEL, "available": True, "max_output_tokens": 128}],
        ):
            with patch.object(rr, "fetch_json", return_value={"models": models}) as network:
                code, _, _ = self.run_cli(["--live", "--approve-api-use"])
                self.assertEqual(code, 1)
                network.assert_called_once_with("/api/catalog")

    def test_live_one_generation_and_key_redaction(self):
        sentinel = "mock-credential-sentinel"
        catalog = {"models": [{"id": "chosen-model", "available": True, "max_output_tokens": 8192}]}
        for interface in rr.PATHS:
            result = rr.mock_response(interface)
            if interface == "chat":
                result["choices"][0]["message"]["content"] = sentinel
            with patch.object(rr, "fetch_json", side_effect=[catalog, result]) as network:
                code, out, err = self.run_cli(
                    ["--interface", interface, "--live", "--approve-api-use"],
                    {"REDROUTER_API_KEY": sentinel, "REDROUTER_MODEL": "chosen-model"},
                )
                self.assertEqual(code, 0)
                self.assertNotIn(sentinel, out + err)
                self.assertEqual(network.call_count, 2)
                self.assertEqual(network.call_args.args[0], rr.PATHS[interface])
                self.assertEqual(network.call_args.args[1]["model"], "chosen-model")

    def test_missing_or_invalid_key_does_not_dispatch_generation(self):
        catalog = {
            "models": [{"id": rr.DEFAULT_MODEL, "available": True, "max_output_tokens": 8192}]
        }
        for key in ("", "bad\nheader", "bad key", "nonascii-\u00e9"):
            with patch.object(rr, "fetch_json", return_value=catalog) as network:
                code, out, err = self.run_cli(
                    ["--live", "--approve-api-use"], {"REDROUTER_API_KEY": key}
                )
                self.assertEqual(code, 1)
                network.assert_called_once_with("/api/catalog")


class Transport(NoNetwork):
    def test_exact_urls_headers_timeouts_and_json(self):
        for interface, path in rr.PATHS.items():
            with patch.object(rr, "build_opener") as build:
                build.return_value.open.return_value.__enter__.return_value.read.return_value = (
                    b"{}"
                )
                payload = rr.make_payload(interface, rr.DEFAULT_MODEL)
                self.assertEqual(rr.fetch_json(path, payload, "mock-only", interface), {})
                request = build.return_value.open.call_args.args[0]
                self.assertEqual(request.full_url, "https://redrouter.org" + path)
                self.assertEqual(request.get_method(), "POST")
                self.assertEqual(json.loads(request.data), payload)
                headers = {k.lower(): v for k, v in request.header_items()}
                self.assertEqual(headers["content-type"], "application/json")
                self.assertEqual(
                    headers["x-api-key" if interface == "messages" else "authorization"],
                    "mock-only" if interface == "messages" else "Bearer mock-only",
                )
                self.assertEqual(build.return_value.open.call_args.kwargs["timeout"], 120)
                self.assertIsInstance(build.call_args.args[1], rr.NoRedirect)
                self.assertEqual(build.call_args.args[0].proxies, {})
                build.return_value.open.assert_called_once()

    def test_catalog_is_unauthenticated_and_keys_cannot_go_elsewhere(self):
        with patch.object(rr, "build_opener") as build:
            build.return_value.open.return_value.__enter__.return_value.read.return_value = b"{}"
            rr.fetch_json("/api/catalog")
            request = build.return_value.open.call_args.args[0]
            self.assertIsNone(request.data)
            self.assertNotIn("authorization", {k.lower() for k, _ in request.header_items()})
        for path in ("https://other.invalid", "/v1/key", "/api/catalog", rr.PATHS["messages"]):
            with self.assertRaises(rr.RequestFailure):
                rr.fetch_json(path, {}, "mock-only", "chat")

    def test_redirects_are_rejected(self):
        with self.assertRaises(rr.RequestFailure):
            rr.NoRedirect().redirect_request(None, None, 302, "moved", {}, "https://other.invalid")

    def test_errors_do_not_leak_bodies_or_retry(self):
        for status in (400, 401, 402, 403, 404, 413, 429, 503):
            body = io.BytesIO(b"reflected-mock-secret")
            error = HTTPError(
                rr.ORIGIN, status, "reflected-mock-secret", {"Retry-After": "5"}, body
            )
            with patch.object(rr, "build_opener") as build:
                build.return_value.open.side_effect = error
                with self.assertRaises(rr.RequestFailure) as caught:
                    rr.fetch_json(rr.PATHS["chat"], {}, "mock-only", "chat")
                self.assertIn(str(status), str(caught.exception))
                self.assertIn("Retry-After: 5s", str(caught.exception))
                self.assertNotIn("reflected-mock-secret", str(caught.exception))
                self.assertEqual(body.tell(), 0)
                build.return_value.open.assert_called_once()
            error.close()

    def test_timeout_invalid_json_and_response_size(self):
        with patch.object(rr, "build_opener") as build:
            build.return_value.open.return_value.__enter__.return_value.read.side_effect = (
                IncompleteRead(b"reflected-mock-secret")
            )
            with self.assertRaisesRegex(rr.RequestFailure, "outcome may be unknown") as caught:
                rr.fetch_json("/api/catalog")
            self.assertNotIn("reflected-mock-secret", str(caught.exception))
        with patch.object(rr, "build_opener") as build:
            build.return_value.open.side_effect = URLError("reflected-mock-secret")
            with self.assertRaisesRegex(rr.RequestFailure, "outcome may be unknown"):
                rr.fetch_json("/api/catalog")
            build.return_value.open.assert_called_once()
        for raw in (b"invalid json", b"\xff", b"x" * (rr.MAX_BYTES + 1)):
            with patch.object(rr, "build_opener") as build:
                build.return_value.open.return_value.__enter__.return_value.read.return_value = raw
                with self.assertRaises(rr.RequestFailure):
                    rr.fetch_json("/api/catalog")


if __name__ == "__main__":
    unittest.main()
