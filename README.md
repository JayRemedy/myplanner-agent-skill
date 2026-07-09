# MyPlanner Agent Skill

A public, copyable agent skill for operating MyPlanner through its REST API and webhooks. The standards-compliant skill identifier is lowercase `myplanner`; `agents/openai.yaml` supplies the user-facing display name `MyPlanner`.

This repository is intentionally small and secret-free. It gives AI agents a stable procedure for discovering board structure, using numeric IDs safely, creating/updating items, handling real subtasks, understanding Agenda as date-column-driven board agenda, and registering HMAC-signed webhooks.

## Install/use with any agent

MyPlanner may give an agent a paste-ready prompt:

```text
$skill-installer install https://github.com/JayRemedy/myplanner-agent-skill/tree/main/skills/myplanner
myplanner_token: plnr_...
```

Expected installation behavior:

1. Invoke `$skill-installer` directly. This is an installation prompt, so do not first check for an existing MyPlanner skill.
2. Install the exact `skills/myplanner` directory from the public repository; do not search the web, inspect branches, or discover another path.
3. The standards identifier/directory is `myplanner`; `agents/openai.yaml` provides the display name `MyPlanner`.
4. Verify the fresh install is visible before saying it is installed.
5. Treat `myplanner_token:` as a current-session MyPlanner API token, not GitHub auth.
6. Verify installation through skill-list visibility. Do not call `GET /me` merely for installation; use the first useful API request, such as `GET /boards`, to verify the token.
7. Under zsh, do not use `status` as a variable; use `http_code` or `scripts/myplanner_api.py`.

If the runtime cannot persistently install the skill, fetch/read `SKILL.md` and continue anyway, but be precise: say “loaded for this session,” not “installed.” Session-loaded instructions may not appear in the skill/slash-command list. Do not stop at “restart” unless the runtime truly cannot use instructions it has already read.

Board names and IDs are never included in this public skill. Agents must call `GET /boards` with the authorized account token before selecting a board. Agenda means the day/calendar agenda generated from a board's Date columns; it is not a separate board or global `/agenda` endpoint.

Examples by runtime:

- Hermes Agent:
  ```bash
  hermes skills install https://raw.githubusercontent.com/JayRemedy/myplanner-agent-skill/main/skills/myplanner/SKILL.md --name myplanner
  hermes -s myplanner
  ```
  Or in an active Hermes session: `/skill myplanner`
- Codex: invoke `$skill-installer` with the exact GitHub directory URL `https://github.com/JayRemedy/myplanner-agent-skill/tree/main/skills/myplanner`.
- Other agents: use the runtime's normal installer for the canonical `skills/myplanner` directory. After install, verify list visibility. Verify the token through the first useful API request.
- If an agent has no skill system: read `skills/myplanner/SKILL.md`, follow Setup and Discovery Workflow, then call the REST API directly.

## Runtime secrets

Do not commit tokens. MyPlanner may give an agent a paste-ready prompt like:

```text
$skill-installer install https://github.com/JayRemedy/myplanner-agent-skill/tree/main/skills/myplanner
myplanner_token: plnr_...
```

Install directly:

- Invoke `$skill-installer` without checking for an existing skill first.
- Install the exact `skills/myplanner` directory; do not search the web or inspect branches.
- Do not treat `myplanner_token` as GitHub auth.
- Verify installation, then wait for or continue with the requested MyPlanner task. Use its first useful API call to verify the token; do not add a standalone `/me` call unless identity information is needed.

Never treat `myplanner_token` as `GITHUB_TOKEN` or any GitHub credential.

After installing the skill, treat the value after `myplanner_token:` as the current-session API token. Use it as `MYPLANNER_API_TOKEN` and use `https://myplanner.dev` as `MYPLANNER_BASE_URL`. For older prompts, `token: plnr_...` means the same thing as `myplanner_token: plnr_...`. If a prompt explicitly includes `myplanner_base_url:`, use it, but MyPlanner's own prompt intentionally omits that line.

Do not commit or persist tokens in this repository, and do not repeat them in final responses. Prefer a private session secret when available. If a token appears in the user's own local terminal echo or command preview but successfully authenticates, continue the requested MyPlanner work in that session; do not refuse or demand a replacement first. Warn once afterward that the user should revoke/replace it. Stop immediately only when authentication fails, the user requests revocation, or there is evidence of disclosure to an untrusted third party. Do not spend multiple attempts building a private stdin wrapper; if stdin is used for the token, do not also deliver the script body through stdin.

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

MyPlanner boards are flexible. Before writing:

1. `GET /boards` (also verifies the token)
2. `GET /boards/{id}`
3. Use numeric `board_id`, `group_id`, `column_id`, `item_id`, and `subtask_id` from API responses.
4. Call `GET /me` only when account identity or token-label information is needed.

Do not infer subtasks from names, indentation, or imported Monday.com shape. An item is a real subtask only if it is returned by `GET /items/{id}/subtasks` or addressed via `/subtasks/{id}`.

## License

MIT
