# RedRouter skill

One [Agent Skill](https://agentskills.io/specification) for configuring RedRouter,
selecting an available model, sending a bounded first request and diagnosing
errors. RedRouter is an inference API with OpenAI-compatible Chat Completions and
Responses and Anthropic-compatible Messages interfaces. It routes to an upstream
provider and offers abliterated and other low-refusal models.

## Prerequisites and installation

- A coding agent that supports Agent Skills.
- Node.js 22.20+ and npm for the current skills CLI; Python 3.10+ for examples.
- For approved live use: a RedRouter account, privately configured
  `REDROUTER_API_KEY`, an eligible trial or credit, and HTTPS access to RedRouter.

Public repository: **[redrouter/examples](https://github.com/redrouter/examples)**. Install:

```sh
npx skills add redrouter/examples --skill redrouter
```

Choose the desired agent interactively. Installation is project-local by default;
add `-g` for global installation. To opt out of CLI telemetry and audit requests:

```sh
DISABLE_TELEMETRY=1 npx skills add redrouter/examples --skill redrouter
```

See [distribution](skill-distribution.md) for listing behavior and verification.
The skill and examples are [MIT licensed](../LICENSE).

## Usage

Run repository commands below from the repository root. Ask your agent: “Configure my app to use RedRouter through Messages” or “Use the
RedRouter skill to diagnose my 429 response without making a live request.”
The installed entrypoint is [skills/redrouter/SKILL.md](../skills/redrouter/SKILL.md).

From the repository root, these examples require no dependencies or key:

```sh
python3 skills/redrouter/scripts/request.py --interface chat
python3 skills/redrouter/scripts/request.py --interface messages
python3 skills/redrouter/scripts/request.py --interface responses
python3 skills/redrouter/scripts/request.py --interface chat --security
```

All default to labeled mocks. The security variant reads only a bundled synthetic
local code sample for potential SQL injection and path traversal; it executes
nothing and makes no live-target requests. Model output needs human verification.

For live use, first read the script and approve one request's content, model and
possible cost/trial consumption. Configure the key privately using a secret store
or hidden terminal prompt; do not type it into shell history or paste it into an
agent conversation. Select a current model through `REDROUTER_MODEL` (default
`red-cyber-1`). An eligible trial is restricted to that model.

Optional smoke test, **only after explicit approval**:

```sh
python3 skills/redrouter/scripts/request.py --interface chat --live --approve-api-use
```

Select `messages` or `responses` for a separate smoke test. Each invocation checks
the public catalog and sends at most one generation, with no retries. Adding
`--security` sends the bundled sample instead of the checksum prompt. The script
rejects redirects and bypasses environment proxies to protect key destinations;
networks requiring a proxy need a separately reviewed client configuration.

The skill does not provide an MCP server, host or modify models, execute tools,
scan targets, guarantee vulnerability findings, or enable every feature of the
original API platforms. It has no signup or usage telemetry of its own. Installing
it does not spend RedRouter credits or authorize a live request.

## Checks and documentation

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-skill-dev.txt
.venv/bin/python -m unittest discover -s tests -v
# Optional unauthenticated public metadata checks; no inference or key access:
.venv/bin/python scripts/check_skill_public.py
```

Tests forbid real network access and validate payloads, parsing, approval guards,
credential destinations, errors and skill structure. The public check validates
all example payloads against the current RedRouter OpenAPI contract. Mocks do not
prove live inference compatibility. See [verified facts](skill-verified-facts.md).

- [Quickstart](https://docs.redrouter.org/quickstart), [authentication](https://docs.redrouter.org/authentication)
- [Compatibility](https://docs.redrouter.org/compatibility), [models](https://redrouter.org/models), [pricing](https://redrouter.org/pricing)
- [Errors](https://docs.redrouter.org/errors), [rate limits](https://docs.redrouter.org/rate-limits)
- [Data handling](https://docs.redrouter.org/data-handling), [privacy](https://redrouter.org/privacy), [terms](https://redrouter.org/terms)
