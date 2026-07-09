# MyPlanner Agent Skill

A public, copyable agent skill for operating MyPlanner through its REST API and webhooks.

This repository is intentionally small and secret-free. It gives AI agents a stable procedure for discovering board structure, using numeric IDs safely, creating/updating items, handling real subtasks, and registering HMAC-signed webhooks.

## Install/use with any agent

MyPlanner may give an agent a paste-ready prompt:

```text
use MyPlanner:
https://raw.githubusercontent.com/JayRemedy/myplanner-agent-skill/main/SKILL.md
myplanner_token: plnr_...
```

Fastest acceptable behavior:

1. The prompt points directly at raw `SKILL.md` on purpose. Fetch/read that Markdown file directly; do not clone the repo, inspect repository layout, check branches, or inspect the current workspace just to use MyPlanner.
2. Treat `myplanner_token:` as the current-session MyPlanner API token, not as a GitHub token.
3. Use `https://myplanner.dev` as the default MyPlanner base URL.
4. Immediately verify with `GET /me`.
5. If the user asked for boards, call `GET /boards` in the same turn.

Do not make persistent skill installation a blocking prerequisite. Persistent install is optional convenience, not the task. If the agent can read these instructions now, it should use them now and continue the requested MyPlanner work. Do not stop at “restart” unless the runtime truly cannot use instructions it has already read. Legacy prompts may say `use https://github.com/JayRemedy/myplanner-agent-skill` or `install https://github.com/JayRemedy/myplanner-agent-skill`; treat those as “read the raw SKILL.md and use it now” unless the user explicitly asks for a persistent install.

Examples by runtime:

- Hermes Agent:
  ```bash
  hermes skills install https://raw.githubusercontent.com/JayRemedy/myplanner-agent-skill/main/SKILL.md --name myplanner
  hermes -s myplanner
  ```
  Or in an active Hermes session: `/skill myplanner`
- Codex, Claude Code, Cursor, Windsurf, Gemini CLI, and similar agents: fetch the raw `SKILL.md` URL from the prompt and use it as custom instructions, project rules, memory, or runtime instructions. If the user included `myplanner_token:`, do the immediate `/me` verification before spending time on persistent installation or cloning.
- If an agent has no skill system: read `SKILL.md`, follow the Setup and Discovery Workflow sections, then call the MyPlanner REST API directly.

## Runtime secrets

Do not commit tokens. MyPlanner may give an agent a paste-ready prompt like:

```text
use MyPlanner:
https://raw.githubusercontent.com/JayRemedy/myplanner-agent-skill/main/SKILL.md
myplanner_token: plnr_...
```

Use fast:

- This repo is public; no GitHub token is needed.
- The prompt points directly at raw `SKILL.md`; fetch/read that file without cloning if possible.
- Do not inspect or modify the current project git state just to use this skill.
- Continue the requested MyPlanner task immediately if the runtime can use the instructions; do not stop at “restart” unless that is truly required.

Never treat `myplanner_token` as `GITHUB_TOKEN` or any GitHub credential.

After installing the skill, treat the value after `myplanner_token:` as the current-session API token. Use it as `MYPLANNER_API_TOKEN` and use `https://myplanner.dev` as `MYPLANNER_BASE_URL`. For older prompts, `token: plnr_...` means the same thing as `myplanner_token: plnr_...`. If a prompt explicitly includes `myplanner_base_url:`, use it, but MyPlanner's own prompt intentionally omits that line.

Do not print, log, commit, or save the token in this repo. If your tool UI shows command previews, avoid pasting the raw token into shell commands; use a redacted secret/session environment or in-memory header where possible. Do not spend multiple attempts building a private stdin wrapper; if stdin is used for the token, do not also deliver the script body through stdin.

```bash
export MYPLANNER_BASE_URL="https://myplanner.dev"
export MYPLANNER_API_TOKEN="plnr_..."
```

If the agent cannot set environment variables, it should still use the pasted token directly in the Bearer authorization header for immediate API calls instead of refusing because `MYPLANNER_API_TOKEN` is not already set.

Tokens are created inside MyPlanner: Settings > Agent access or `Integrate` > `API tokens`.

## REST entrypoint

```text
https://myplanner.dev/app/rest.php
```

Example:

```bash
curl -sS \
  -H "Authorization: Bearer $MYPLANNER_API_TOKEN" \
  "$MYPLANNER_BASE_URL/app/rest.php/boards"
```

## Important agent rule

MyPlanner boards are flexible. An agent must inspect the live board before writing:

1. `GET /me`
2. `GET /boards`
3. `GET /boards/{id}`
4. Use numeric `board_id`, `group_id`, `column_id`, `item_id`, and `subtask_id` from API responses.

Do not infer subtasks from names, indentation, or imported Monday.com shape. An item is a real subtask only if it is returned by `GET /items/{id}/subtasks` or addressed via `/subtasks/{id}`.

## License

MIT
