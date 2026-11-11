import json
import unittest
from pathlib import Path

import httpx2 as httpx
from openai import OpenAI

from python.triage import read_evidence, triage

REPORT = json.loads((Path(__file__).resolve().parents[1] / "python/findings.json").read_text())


class TriageTests(unittest.TestCase):
    def test_tool_round_trip_preserves_call_id_and_returns_report(self):
        requests = []

        def respond(request):
            body = json.loads(request.content)
            self.assertEqual(str(request.url), "https://redrouter.org/v1/chat/completions")
            self.assertEqual(body["model"], "glm-5.3-flash-red")
            self.assertLessEqual(body["max_tokens"], 2000)
            requests.append(body)
            if len(requests) == 1:
                message = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_evidence",
                            "type": "function",
                            "function": {
                                "name": "read_evidence",
                                "arguments": '{"evidence_id":"E-01"}',
                            },
                        }
                    ],
                }
            else:
                self.assertEqual(
                    body["messages"][-1],
                    {
                        "role": "tool",
                        "tool_call_id": "call_evidence",
                        "content": REPORT["evidence"]["E-01"],
                    },
                )
                message = {"role": "assistant", "content": "F-01: verify account scope (E-01)."}
            return httpx.Response(
                200,
                json={
                    "id": "fixture",
                    "object": "chat.completion",
                    "created": 0,
                    "model": "glm-5.3-flash-red",
                    "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
                },
            )

        with OpenAI(
            api_key="fixture-key",
            base_url="https://redrouter.org/v1",
            http_client=httpx.Client(transport=httpx.MockTransport(respond)),
            max_retries=0,
        ) as client:
            self.assertIn("E-01", triage(client, REPORT))
        self.assertEqual(len(requests), 2)

    def test_unknown_tools_ids_and_extra_arguments_fail_closed(self):
        for name, arguments in [
            ("run_shell", '{"evidence_id":"E-01"}'),
            ("read_evidence", '{"evidence_id":"../../secret"}'),
            ("read_evidence", '{"evidence_id":"E-01","command":"pwd"}'),
            ("read_evidence", '{"evidence_id":[]}'),
        ]:
            with self.subTest(name=name, arguments=arguments), self.assertRaises(ValueError):
                read_evidence(name, arguments, REPORT["evidence"])

    def test_repeated_tool_calls_stop_after_four_requests(self):
        requests = []

        def respond(request):
            body = json.loads(request.content)
            requests.append(body)
            return httpx.Response(
                200,
                json={
                    "id": "fixture",
                    "object": "chat.completion",
                    "created": 0,
                    "model": "glm-5.3-flash-red",
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "tool_calls",
                            "message": {
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [
                                    {
                                        "id": f"call_{len(requests)}",
                                        "type": "function",
                                        "function": {
                                            "name": "read_evidence",
                                            "arguments": '{"evidence_id":"E-01"}',
                                        },
                                    }
                                ],
                            },
                        }
                    ],
                },
            )

        with (
            OpenAI(
                api_key="fixture-key",
                base_url="https://redrouter.org/v1",
                http_client=httpx.Client(transport=httpx.MockTransport(respond)),
                max_retries=0,
            ) as client,
            self.assertRaisesRegex(RuntimeError, "budget"),
        ):
            triage(client, REPORT)
        self.assertEqual(len(requests), 4)
        self.assertEqual(requests[-1]["tool_choice"], "none")


if __name__ == "__main__":
    unittest.main()
