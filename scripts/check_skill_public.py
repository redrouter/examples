"""Optional metadata-only contract check. Never reads keys or calls inference."""

import importlib.util
import json
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from jsonschema import Draft202012Validator

spec = importlib.util.spec_from_file_location(
    "skill_request", Path(__file__).resolve().parents[1] / "skills/redrouter/scripts/request.py"
)
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)

SPEC_URL = "https://docs.redrouter.org/openapi.json"


def validate_examples(spec, catalog):
    model = next(m for m in catalog["models"] if m["id"] == rr.DEFAULT_MODEL and m["available"])
    checked = 0
    for interface, path in rr.PATHS.items():
        operation = spec["paths"][path]["post"]
        if {"bearerAuth": []} not in operation["security"]:
            raise ValueError(f"Bearer authentication contract changed for {path}")
        if interface == "messages" and {"apiKey": []} not in operation["security"]:
            raise ValueError("Messages x-api-key authentication contract changed")
        wire_schema = operation["requestBody"]["content"]["application/json"]["schema"]
        schema = {**wire_schema, "components": spec["components"]}
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        for security in (False, True):
            payload = rr.make_payload(interface, rr.DEFAULT_MODEL, security)
            validator.validate(payload)
            if (
                payload.get("max_tokens", payload.get("max_output_tokens"))
                > model["max_output_tokens"]
            ):
                raise ValueError("Example output budget exceeds current catalog limit")
            checked += 1
    if (
        catalog["api_base_url"] != "https://redrouter.org/v1"
        or catalog["anthropic_base_url"] != "https://redrouter.org"
    ):
        raise ValueError("Canonical base URL changed")
    schemes = spec["components"]["securitySchemes"]
    if schemes["bearerAuth"]["scheme"] != "bearer" or schemes["apiKey"]["name"] != "x-api-key":
        raise ValueError("Authentication scheme changed")
    return checked


def main():
    catalog = rr.fetch_json("/api/catalog")
    with build_opener(ProxyHandler({}), rr.NoRedirect()).open(
        Request(SPEC_URL, headers={"Accept": "application/json"}), timeout=30
    ) as response:
        raw = response.read(rr.MAX_BYTES + 1)
    if len(raw) > rr.MAX_BYTES:
        raise ValueError("OpenAPI document too large")
    count = validate_examples(json.loads(raw), catalog)
    print(
        f"PASS: {count} payloads match current public OpenAPI; "
        "model, base URLs and auth verified. No inference or key access."
    )


if __name__ == "__main__":
    main()
