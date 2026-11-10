# Verification snapshot

Checked 2026-11-07 using unauthenticated public reads of the
[complete docs](https://docs.redrouter.org/llms-full.txt),
[OpenAPI](https://docs.redrouter.org/openapi.json),
[catalog](https://redrouter.org/api/catalog),
[pricing](https://redrouter.org/pricing),
[privacy](https://redrouter.org/privacy) and [terms](https://redrouter.org/terms).
These are dated observations, not permanent promises. Recheck before changing
client features or estimating spend. No inference request was made.

The product repository's registered routes and Messages authentication adapter
matched the public contract. All 17 catalog model IDs, context/output limits and
retail prices matched the repository's model configuration.

| Verified contract | Result |
| --- | --- |
| Canonical OpenAI SDK base | `https://redrouter.org/v1` |
| Canonical Anthropic SDK base | `https://redrouter.org` |
| Generation | `POST /v1/chat/completions`, `/v1/responses`, `/v1/messages` |
| Public metadata | `GET /api/catalog` without credentials |
| Key diagnostics / model list | `GET /v1/key`, `GET /v1/models` with Bearer auth |
| Messages authentication | `x-api-key` also accepted; Bearer takes precedence |
| Text / streaming / client tools | Documented on all three interfaces |
| Images / structured output | Model-dependent; inspect catalog capabilities |
| Hosted tools / persisted Responses | Unsupported; clients manage history and tool execution |
| Reasoning / cache hints | Documented accepted shapes can be ignored; cache rates require reported hits |

The catalog reported 17 available exact IDs:

```text
red-cyber-1
glm-5.3-flash-rr
glm-5.3-rr
qwen3.8-27b-rr
deepseek-v4.1-flash-rr
deepseek-v4.1-flash-1017
deepseek-v4.1-flash-0910
glm-5.3-flash
glm-5.3
qwen3.8-27b
deepseek-v4-flash-0731
deepseek-v4-flash-0423
mimo-v2.6-flash
step-5-preview
hy4-preview
nemotron-3-ultra
minimax-m3.1-flash
```

The example model `red-cyber-1` reported $0.25 input, $0.08 cached input and $1.00
output per million tokens, 1,048,576 context and 8,192 max output tokens, with tools
and response formats but no image input. `glm-5.3-flash-rr` reported $0.20 / $0.08 /
$0.80 respectively, with the same context/output limits. GLM 5.3 RR reported a
32,768-token output limit and no response-format capability. Do not infer feature
equivalence or a particular weight revision from a family name or RR suffix.
The catalog's explicit capability flags override generic examples.

Eligible accounts receive ten upstream-dispatched trial generations shared by
Chat and API, only on `red-cyber-1`; retries/tool turns consume additional requests.
Otherwise usage requires credit. Price and limits are account/model-dependent;
use the live catalog and Settings for effective values. Some generic docs still
say funded-only or describe older output limits; the specific trial guide and
catalog are more precise. Do not copy those generic claims into client behavior.

New API keys have request-content storage off; existing keys can retain it on.
Account Zero Data Retention is separately opt-in, disables Save chat, and retains
billing metadata. Eligibility and plan requirements are maintained in the
[data-handling guide](https://docs.redrouter.org/data-handling); verify access in
Settings before relying on it. It applies to subsequent requests. Where enabled,
content storage is encrypted for up to 30 days; the data-handling guide permits
backup copies for seven additional days.
RedRouter forwards content to inference infrastructure and cannot independently
verify its retention. Neither a Responses `store: false` field nor a new key
establishes account-wide or upstream Zero Data Retention.

Live service behavior still needs explicitly approved smoke tests. The optional
public check verifies payload schemas and catalog facts, not supplier execution,
capacity, billing accuracy or model quality.
