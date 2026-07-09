# MyPlanner Agent Skill

A public, copyable agent skill for operating MyPlanner through its REST API and webhooks.

This repository is intentionally small and secret-free. It gives AI agents a stable procedure for discovering board structure, using numeric IDs safely, creating/updating items, handling real subtasks, and registering HMAC-signed webhooks.

## Install in Hermes Agent

```bash
hermes skills install https://raw.githubusercontent.com/JayRemedy/myplanner-agent-skill/main/SKILL.md --name myplanner
```

Then start a new session and load the skill:

```bash
hermes -s myplanner
```

Or in an active session:

```text
/skill myplanner
```

## Use with other agents

If your agent does not support Hermes skills directly, copy `SKILL.md` into the agent's custom instructions, memory, or project rules.

## Runtime secrets

Do not commit tokens. Give the agent these at runtime through environment variables or your agent platform's secret store:

```bash
export MYPLANNER_BASE_URL="https://myplanner.dev"
export MYPLANNER_API_TOKEN="your-token-here"
```

Tokens are created inside MyPlanner: `Integrate` > `API tokens`.

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
