import contextlib
import io
import json
import os
import unittest
from unittest.mock import patch

import httpx2 as httpx
from anthropic import Anthropic
from openai import OpenAI

from python import chat, messages


class SDKExamplesTests(unittest.TestCase):
    def test_python_examples_use_redrouter_paths_key_and_model(self):
        for module, sdk, path in [
            (chat, OpenAI, "/v1/chat/completions"),
            (messages, Anthropic, "/v1/messages"),
        ]:
            with self.subTest(path=path):
                requests = []

                def respond(request):
                    self.assertEqual(request.url.host, "redrouter.org")
                    self.assertEqual(request.url.path, path)
                    self.assertTrue(
                        request.headers.get("authorization") == "Bearer fixture-key"
                        or request.headers.get("x-api-key") == "fixture-key"
                    )
                    body = json.loads(request.content)
                    self.assertEqual(body["model"], "glm-5.3-flash-red")
                    self.assertEqual(body["max_tokens"], 256)
                    requests.append(body)
                    if module is chat:
                        data = {
                            "id": "fixture",
                            "object": "chat.completion",
                            "created": 0,
                            "model": "glm-5.3-flash-red",
                            "choices": [
                                {
                                    "index": 0,
                                    "finish_reason": "stop",
                                    "message": {
                                        "role": "assistant",
                                        "content": "Review account scope.",
                                    },
                                }
                            ],
                        }
                    else:
                        data = {
                            "id": "fixture",
                            "type": "message",
                            "role": "assistant",
                            "model": "glm-5.3-flash-red",
                            "stop_reason": "end_turn",
                            "content": [{"type": "text", "text": "Review account scope."}],
                            "usage": {"input_tokens": 10, "output_tokens": 4},
                        }
                    return httpx.Response(200, json=data)

                def make_client(**kwargs):
                    return sdk(
                        **kwargs,
                        http_client=httpx.Client(transport=httpx.MockTransport(respond)),
                    )

                output = io.StringIO()
                with (
                    patch.dict(os.environ, REDROUTER_API_KEY="fixture-key"),
                    patch.object(
                        module,
                        sdk.__name__,
                        side_effect=make_client,
                    ),
                    contextlib.redirect_stdout(output),
                ):
                    module.main()
                self.assertEqual(output.getvalue(), "Review account scope.\n")
                self.assertEqual(len(requests), 1)


if __name__ == "__main__":
    unittest.main()
