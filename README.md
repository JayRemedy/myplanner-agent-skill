# MyPlanner Agent Skill

A public, copyable agent skill for operating MyPlanner through its REST API and webhooks. The standards-compliant skill identifier is lowercase `myplanner`; `agents/openai.yaml` supplies the user-facing display name `MyPlanner`.

This repository is intentionally small and secret-free. It gives AI agents a stable procedure for discovering board structure, using numeric IDs safely, creating/updating items, handling real subtasks, understanding Agenda as date-column-driven board agenda, and registering HMAC-signed webhooks.

## Install/use with any agent

MyPlanner may give an agent a paste-ready prompt:

```text
install https://github.com/JayRemedy/myplanner-agent-skill directly (root SKILL.md; no web search; do not echo token)
myplanner_token: plnr_...
```

Expected fast behavior:

1. Check whether `/MyPlanner` is already installed. If yes, skip the installer, GitHub inspection, web search, and local file rewrites; immediately verify `GET /me`.
2. Only if unavailable, install/register this public repo using the runtime's normal installer. The skill is the root `SKILL.md`; no GitHub auth, branch inspection, or subdirectory discovery is needed.
3. Use `MyPlanner` as the display/name so the preferred command is `/MyPlanner`; keep lowercase `myplanner` as an alias when supported.
4. Verify a fresh install is visible in the normal skill/slash-command list before saying it is installed.
5. Treat `myplanner_token:` as the current-session MyPlanner API token, not as a GitHub token.
6. Use `https://myplanner.dev` as the default base URL and immediately verify `GET /me`; call `GET /boards` in the same turn when boards are relevant.
7. Under zsh, do not use `status` as a variable name. Use `http_code` or the bundled `scripts/myplanner_api.py` helper.

If the runtime cannot persistently install the skill, fetch/read `SKILL.md` and continue anyway, but be precise: say “loaded for this session,” not “installed.” Session-loaded instructions may not appear in the skill/slash-command list. Do not stop at “restart” unless the runtime truly cannot use instructions it has already read.

Known board names from the latest verified workspace: JunkDoctors, Bunker, Bapi, Liabilities, and myplanner. The skill still tells agents to call `GET /boards` before writes. Agenda means the day/calendar agenda generated from a board's Date columns; it is not a separate board or global `/agenda` endpoint.

Examples by runtime:

- Hermes Agent:
  ```bash
  hermes skills install https://raw.githubusercontent.com/JayRemedy/myplanner-agent-skill/main/SKILL.md --name myplanner
  hermes -s myplanner
  ```
  Or in an active Hermes session: `/skill myplanner`
- Codex, Claude Code, Cursor, Windsurf, Gemini CLI, and similar agents: use the runtime's normal installer/custom-instruction flow for this GitHub repo if available. After install, verify the skill appears in the normal skill/slash-command list before claiming it is installed. Then do the immediate `/me` verification before stopping.
- If an agent has no skill system: read `SKILL.md`, follow the Setup and Discovery Workflow sections, then call the MyPlanner REST API directly.

## Runtime secrets

Do not commit tokens. MyPlanner may give an agent a paste-ready prompt like:

```text
install https://github.com/JayRemedy/myplanner-agent-skill directly (root SKILL.md; no web search; do not echo token)
myplanner_token: plnr_...
```

Connect quickly:

- If `/MyPlanner` is already installed, do not reinstall or inspect GitHub; use it immediately.
- Otherwise install/register this public repo with the runtime's normal skill installer. The skill is the root `SKILL.md`.
- Do not treat `myplanner_token` as GitHub auth.
- Verify a fresh install is visible before claiming it is installed.
- Continue immediately with `GET /me`, then the requested MyPlanner task.

Never treat `myplanner_token` as `GITHUB_TOKEN` or any GitHub credential.

After installing the skill, treat the value after `myplanner_token:` as the current-session API token. Use it as `MYPLANNER_API_TOKEN` and use `https://myplanner.dev` as `MYPLANNER_BASE_URL`. For older prompts, `token: plnr_...` means the same thing as `myplanner_token: plnr_...`. If a prompt explicitly includes `myplanner_base_url:`, use it, but MyPlanner's own prompt intentionally omits that line.

Do not print, log, commit, or save the token in this repo. If your tool UI shows command previews, avoid pasting the raw token into shell commands; use a redacted secret/session environment or in-memory header where possible. Do not spend multiple attempts building a private stdin wrapper; if stdin is used for the token, do not also deliver the script body through stdin.

```bash
export MYPLANNER_BASE_URL="https://myplanner.dev"
export MYPLANNER_API_TOKEN="plnr_..."
```

If the agent cannot set environment variables, it should still use the pasted token directly in the Bearer authorization header for immediate API calls instead of refusing because `MYPLANNER_API_TOKEN` is not already set.

For a deterministic call path that avoids shell-variable mistakes, use the dependency-free helper bundled with the skill:

```bash
python3 scripts/myplanner_api.py GET /me
python3 scripts/myplanner_api.py GET /boards
```

It reads `MYPLANNER_API_TOKEN`; `--token-stdin` is available when the runtime can provide stdin securely. Under zsh, never name a variable `status`; use `http_code`.

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
