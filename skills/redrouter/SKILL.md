---
name: redrouter
license: MIT
description: Configure and troubleshoot RedRouter inference for an existing app or coding agent using its OpenAI-compatible Chat Completions or Responses API, or Anthropic-compatible Messages API. Use when the user asks to connect RedRouter, choose a RedRouter model, send a first request, diagnose API errors, or review authorized local code through RedRouter.
metadata:
  author: RedRouter
  version: "1.0.0"
---

# RedRouter

Bundled examples require Python 3.10+; approved live use requires HTTPS access to
redrouter.org. No SDK is required.

Help the user get a working, bounded inference request. RedRouter routes inference
through an upstream provider and offers abliterated and other low-refusal models;
do not describe RedRouter as hosting models or performing model abliteration itself.

## Configure

1. Read the [current compatibility matrix](https://docs.redrouter.org/compatibility)
   for the client's features. Preserve unrelated client settings. Use:

   | Client interface | SDK base URL | HTTP generation route | Authentication |
   | --- | --- | --- | --- |
   | OpenAI Chat Completions | `https://redrouter.org/v1` | `POST /v1/chat/completions` | `Authorization: Bearer …` |
   | OpenAI Responses | `https://redrouter.org/v1` | `POST /v1/responses` | `Authorization: Bearer …` |
   | Anthropic Messages | `https://redrouter.org` | `POST /v1/messages` | `x-api-key: …` or Bearer |

   Messages clients append `/v1/messages`; do not double `/v1`. If both auth
   headers are present, Authorization takes precedence. For agent-specific setup,
   follow the current [integration guides](https://docs.redrouter.org/integrations).

2. Have the user create a key in [API Keys](https://redrouter.org/keys) and set
   `REDROUTER_API_KEY` privately through their secret store or hidden terminal
   prompt. Never ask them to paste it into chat. Do not inspect, print, embed, commit,
   or send the key to another service; an approved client reads it from the
   environment. Do not put it in URLs, browser code, command arguments, debug
   traces, or saved request bodies. Use environment references
   in generated configuration; disable SDK automatic retries for the first test.

3. Fetch the public [catalog](https://redrouter.org/api/catalog) without a key.
   Choose an exact `models[].id` with `available: true`, suitable capabilities,
   context/output limits and retail `pricing`. Confirm it is permitted by the
   key. Do not silently change an existing model. `red-cyber-1` is the example
   and eligible-trial model; recheck availability rather than treating it as
   permanent. Other models require credit. Cached pricing applies only to
   reported cache reads. See [model selection](https://docs.redrouter.org/model-selection).

4. Before sensitive input, review [data handling](https://docs.redrouter.org/data-handling).
   New keys default to `store_content: false`; older keys may store content.
   Account Zero Data Retention is opt-in in Settings, covers subsequent API/Chat
   requests, disables Save chat, and adds 20% to token prices outside paid monthly
   plan periods. Billing metadata remains. These controls describe RedRouter's
   retention; upstream retention is not independently verified. Minimize inputs.

## First request

Resolve paths below relative to this skill directory. Start offline:

```sh
python3 scripts/request.py --interface chat
python3 scripts/request.py --interface messages
python3 scripts/request.py --interface responses
```

These print clearly labeled fixtures and never read a key or access the network.
Inspect [scripts/request.py](scripts/request.py) for minimal JSON payloads and
response parsing. Set `REDROUTER_MODEL` to the chosen catalog ID if needed.

Only after the user explicitly approves a request that may spend credits or trial
quota, run **one** selected interface with `--live --approve-api-use`. The flags
are an execution guard, not permission for an agent to approve itself. The script
checks the public catalog, then sends one non-streaming generation, with no
automatic retries. It reads the key only in live mode and only sends it to the
fixed RedRouter generation route. `GET /v1/key` can diagnose a key's settings,
but also needs approval before transmitting the key.

Use `max_tokens` for Chat and Messages; Messages requires it. Responses uses
`max_output_tokens`. Confirm a complete terminal status and nonempty text;
unknown usage is not zero usage. The fixtures do not establish live compatibility.

## Authorized security review

For a local review, use the bundled synthetic, sanitized sample:

```sh
python3 scripts/request.py --interface chat --security
```

With explicit API-use approval, the same command plus the live flags sends only
that sample for analysis of potential vulnerabilities, mitigations and local
regression-test suggestions. It never runs the sample, scans a repository,
contacts a target, or executes model-suggested commands. Read
[assets/sanitized_sample.py](assets/sanitized_sample.py) before dispatch. For real
code, establish authorization and the exact content to send, remove credentials
and personal data, and obtain approval for that content. Treat findings as
hypotheses to verify locally; do not claim exploit validation.

## Troubleshoot

| Result | Action |
| --- | --- |
| 400 | Check supported fields, JSON shape, model capabilities and context. Do not pass every SDK option through. |
| 401 | Check the variable is set without displaying it; verify active/unexpired key and correct auth header. Replace expired/revoked keys. |
| 402; credit-related 403 on Messages | Check credit and in-flight holds, or lower output budget. Eligible trials allow only `red-cyber-1`; trial quota is shared with Chat. |
| Other 403 | Check paused key, allowlist, key spending limit and account/trial restrictions. |
| 404 | Verify exact catalog ID and route; fix duplicated `/v1`. |
| 408 / 413 | Reduce upload time / serialized body size; token context and byte limits are separate. |
| 429 | Honor `Retry-After`; reduce rate/concurrency. Daily spend resets at 00:00 UTC; key limits have their own reset. |
| 503 | Check capacity/availability and `Retry-After`; do not silently substitute models. |
| Timeout, disconnect, partial output | Outcome may be billable. Check Usage before another attempt; never blindly retry. |
| Empty/truncated text | Check finish reason/status and output budget, including reasoning tokens. Never execute partial tool calls. |

Chat/Responses errors expose `error.code`; Messages usually exposes only
`error.type` and message. Record status, safe error category and `x-request-id`,
never credentials, raw error bodies or sensitive content. Follow
[errors](https://docs.redrouter.org/errors),
[rate limits](https://docs.redrouter.org/rate-limits), and
[troubleshooting](https://docs.redrouter.org/troubleshooting) for persistent issues.

Compatibility is scoped: text, streaming and client-executed tools are documented;
image and structured-output support vary by model. Clients manage conversation
history. Hosted web/shell/code execution, stored Responses retrieval, embeddings,
audio, fine-tuning and batch APIs are outside the documented contract. Accepted
reasoning/cache hints do not guarantee the requested behavior. Read the relevant
guide before adding features; this skill does not grant target-testing permission.
