<p align="center"><img src="assets/logo.svg" width="76" height="76" alt="RedRouter"></p>
<h1 align="center">RedRouter examples</h1>
<p align="center">Useful starting points.</p>

[RedRouter](https://redrouter.org) is a low-refusal inference API for authorized security work. These examples use `glm-5.3-flash-red` through OpenAI-compatible Chat Completions or Anthropic-compatible Messages. Copy a request, connect your SDK, or triage a fictional security report with a read-only tool.

## In 30 seconds

Create an [API key](https://redrouter.org/keys), add [credits](https://redrouter.org/credits), then run:

```sh
export REDROUTER_API_KEY="YOUR_REDROUTER_API_KEY"
sh curl/chat.sh
```

Requests use credits. Never commit your key.

## Pick an example

| Example | Run from this directory |
| --- | --- |
| [curl](curl/chat.sh) | `sh curl/chat.sh` |
| [Python · OpenAI SDK](python/chat.py) | `python python/chat.py` |
| [TypeScript · OpenAI SDK](typescript/chat.ts) | `npm run chat` |
| [Python · Anthropic SDK](python/messages.py) | `python python/messages.py` |
| [Claude Code](claude-code/run.sh) | `sh claude-code/run.sh` |
| [Report triage · tool calling](python/triage.py) | `python python/triage.py` |

Python: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt` (Python 3.11+).

TypeScript: `npm ci` (Node.js 22+). Claude Code must already be installed; its wrapper selects RedRouter without changing your saved configuration.

Triage reads bundled fictional findings. Its only tool retrieves known evidence IDs; it cannot execute commands or contact targets. Review its conclusions before acting. Use these examples only for [authorized work](SECURITY.md).

## Check locally

```sh
pip install -r requirements-dev.txt
ruff check . && ruff format --check .
python -m unittest discover -s tests
npm ci && npm run check
```

Checks make no paid requests. See the [API documentation](https://docs.redrouter.org) and [MIT license](LICENSE).


## RedRouter agent skill

Install one useful skill for configuring RedRouter, choosing an available model,
making a first request, and troubleshooting API errors:

```sh
npx skills add redrouter/examples --skill redrouter
```

The current skills CLI requires Node.js 22.20+. Bundled skill examples require
Python 3.10+ and no SDK. They default to labeled mocks and do not read a key or
access the network:

```sh
python3 skills/redrouter/scripts/request.py --interface chat
python3 skills/redrouter/scripts/request.py --interface messages
python3 skills/redrouter/scripts/request.py --interface responses
python3 skills/redrouter/scripts/request.py --interface chat --security
```

The skill covers both compatibility interfaces and a defensive review of a
bundled synthetic local code sample. It does not execute tools, scan targets,
host or modify models, or grant permission for security testing. Live examples
require a privately configured `REDROUTER_API_KEY`, an available model and credit
or eligible trial, plus explicit API-use approval. Installation does not authorize
inference or spend credits. RedRouter routes inference through an upstream provider;
account Zero Data Retention is opt-in. Review the
[data-handling policy](https://docs.redrouter.org/data-handling) before sensitive input.

See the [skill](skills/redrouter/SKILL.md) and
[complete usage guide](docs/agent-skill.md) for approval guards, optional live smoke
tests, prerequisites, documentation links and telemetry opt-out. The skill has no
tracking code of its own; [skills.sh discovery](docs/skill-distribution.md) uses
installation telemetry. For skill checks, install `requirements-skill-dev.txt`,
then run `python -m unittest discover -s tests`.

Model discovery is public: `curl https://redrouter.org/v1/models` requires no API key.
