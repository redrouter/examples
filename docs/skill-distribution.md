# Distribution through skills.sh

Verified 2026-11-07 against the [official FAQ](https://skills.sh/docs/faq),
[CLI docs](https://skills.sh/docs/cli), and the CLI's
[creating guide](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md),
[installation guide](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
and [telemetry configuration](https://github.com/vercel-labs/skills/blob/main/docs/troubleshooting.md).
Recheck these before release; no installation was run during preparation.

The public GitHub repository is `redrouter/examples`, with one MIT-licensed skill:

```text
README.md
requirements-skill-dev.txt
docs/agent-skill.md
docs/skill-distribution.md
docs/skill-verified-facts.md
scripts/check_skill_public.py
tests/test_skill.py
skills/redrouter/
  SKILL.md
  scripts/request.py
  assets/sanitized_sample.py
```

`skills/<name>/SKILL.md` is a standard discovery location. Its YAML name matches
its containing directory. No plugin manifest or special registration file is
needed. Supporting scripts and assets live inside the skill so installation keeps
it self-contained. Repository development checks stay outside the installed skill.

The official FAQ says skills enter the leaderboard automatically through CLI
installation telemetry. Publishing a repository alone does not establish a
listing. A telemetry-enabled `npx skills add redrouter/examples --skill redrouter`
is the documented installation/discovery path, not a manual submission process.
That supports expected discovery; it does not guarantee immediate indexing,
placement, an official badge, a search ranking or an SEO benefit.

The CLI sends installation telemetry and may make security-audit requests for
confirmed public GitHub repositories. `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1`
disables both. An opted-out installation can install the skill successfully but
does not supply the documented telemetry signal for leaderboard discovery.
The official site describes aggregate anonymous installs; consult the current
CLI documentation/source for exact transmitted fields rather than promising
that no metadata ever leaves the machine.

After approval and publication:

1. Confirm GitHub serves `skills/redrouter/SKILL.md` publicly with the right name
   and supporting files, including the MIT license.
2. In a disposable project, run the approved installation command and inspect the
   installed files and agent discovery. Use opt-out for private QA; obtain separate
   approval before any telemetry-enabled install intended to trigger discovery.
3. After a real approved telemetry-enabled install, check the expected detail URL
   `https://skills.sh/redrouter/examples/redrouter` and search the site for the exact
   source and skill name. These are verification targets, not an existing listing.
4. Verify the page's GitHub source, rendered instructions and install count. If
   absent, recheck public accessibility, frontmatter, CLI version and opt-out
   settings, allow indexing time, and use the directory's support channel if needed.
   Do not manufacture install counts or repeatedly install to influence ranking.

No repository creation, push, deployment, listing submission, telemetry-enabled
installation or live inference is part of the automated checks.
