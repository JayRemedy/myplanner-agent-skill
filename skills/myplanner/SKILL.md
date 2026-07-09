---
name: myplanner
description: Use when an agent needs to read, update, sync, or automate MyPlanner boards, agenda, tasks, subtasks, Monday imports, REST API access, and webhooks.
license: MIT
compatibility: Requires HTTPS access to myplanner.dev and either Python 3, curl, or an authenticated HTTP request tool.
metadata:
  version: "1.2.0"
  author: "JayRemedy"
  aliases: "myplanner, Myplanner"
  preferred_slash_command: "/MyPlanner"
  hermes:
    tags: "MyPlanner, myplanner, boards, agenda, tasks, subtasks, rest-api, webhooks, planning"
    homepage: "https://myplanner.dev"
---

# MyPlanner Agent Skill

## Overview

MyPlanner is a planning-board app with boards, groups, items, columns, updates, subtasks, Google Calendar sync settings, REST API tokens, and HMAC-signed webhooks.

Use this skill when you need to let an AI agent operate a MyPlanner workspace safely: list boards, inspect structure, create or update tasks, maintain column values, backfill missing text, sync imported Monday.com data, or register webhooks.

The most important rule: inspect the live board structure first. MyPlanner boards are flexible. Column IDs, group IDs, and item IDs are numeric and board-specific, so do not guess them from names.

## Known workspace concepts

Boards are top-level MyPlanner workspaces. As of the latest verified `/boards` response, John's workspace contains these boards:

| ID | Board |
| --- | --- |
| 4 | JunkDoctors |
| 3 | Bunker |
| 2 | Bapi |
| 1 | Liabilities |
| 7 | myplanner |

Use these as helpful defaults for recognition and routing, but still call `GET /boards` before writes because board IDs/names can change.

Agenda is not a separate board. In the app UI, Agenda means the calendar/day agenda derived from the currently opened board's Date columns. It lists items and subtasks whose date-column value matches the selected day/today, including group, date-column title when multiple Date columns exist, status, and subtask marker. To answer agenda questions through the REST API: fetch/verify the target board, identify `date` columns, fetch items and subtasks as needed, parse date values, then filter by the requested date. If the user just says “agenda” without a board, ask which board or use the currently implied board from context; do not invent a global `/agenda` endpoint.

## Setup

MyPlanner may give you a paste-ready install prompt like:

```text
$skill-installer install https://github.com/JayRemedy/myplanner-agent-skill/tree/main/skills/myplanner
myplanner_token: plnr_...
```

Installation path for pasted prompts:

1. This prompt is specifically for a fresh installation. Invoke the named `$skill-installer` directly; do not first check whether MyPlanner is already installed.
2. The URL points to the exact canonical skill directory. Install that directory directly; do not search the web, inspect repository branches, or discover another skill path.
3. The repository is public. Do not use the pasted `myplanner_token` as `GITHUB_TOKEN`; it is only a MyPlanner API credential.
4. The standards-compliant skill identifier and directory are lowercase `myplanner`. `agents/openai.yaml` supplies the user-facing display name `MyPlanner`.
5. Verify list visibility before saying the persistent install succeeded. If the runtime cannot install persistently, read the canonical `SKILL.md` and say “loaded for this session,” not “installed.”
6. Use `https://myplanner.dev` as `MYPLANNER_BASE_URL`, then verify `GET /me` immediately. If board access is relevant, call `GET /boards` in the same turn.
7. Under zsh, never use the variable name `status`; use `http_code` or the bundled `scripts/myplanner_api.py` helper.

Do not commit the token, save it in this skill repo, log it, expose it in final output, or paste it into a shell command line if your tool UI shows command previews. Prefer your runtime's secret/session environment facility. If a command preview would reveal the raw token, use an API client/header facility that redacts secrets or keep the token in memory. Do not spend multiple attempts building a “private stdin” wrapper; if your tool cannot pass the token privately, make the minimal verified call, avoid echoing it in the answer, and tell the user to revoke the short-lived/exposed token afterward. If you do use stdin for the token, do not also deliver the Python/script body through stdin; use `python -c` or a temp script so stdin remains available for the token.

For shell calls where command previews are private/redacted, provide the credential through the command environment or an in-memory/session export, for example:

```bash
export MYPLANNER_BASE_URL="https://myplanner.dev"
export MYPLANNER_API_TOKEN="plnr_..."
```

If your runtime has a secure secret store, save the token there instead. If you cannot set environment variables, still use the pasted token directly in the Bearer authorization header for the immediate API call; do not refuse just because the token is not already present in the process environment.

If no token was pasted, ask the user to generate one in MyPlanner Settings > Agent access or Integrate > API tokens.

Tokens authenticate with:

```http
Authorization header with a Bearer token
```

The REST entrypoint is:

```text
/app/rest.php
```

Most servers support path-style routes such as:

```text
https://myplanner.dev/app/rest.php/boards
```

If a host strips `PATH_INFO`, use the fallback query form:

```text
https://myplanner.dev/app/rest.php?path=/boards
```

## Quick API Helper

Prefer the bundled dependency-free helper so the agent does not need to invent shell validation code:

```bash
python3 scripts/myplanner_api.py GET /me
python3 scripts/myplanner_api.py GET /boards
python3 scripts/myplanner_api.py POST /boards/123/items '{"name":"New item"}'
```

It reads `MYPLANNER_API_TOKEN` and defaults to `https://myplanner.dev`. It also supports `--token-stdin` when the runtime can provide stdin without exposing the token in command previews.

Direct `curl` is also supported:

```bash
curl -sS \
  -H "Authorization: Bearer $MYPLANNER_API_TOKEN" \
  "$MYPLANNER_BASE_URL/app/rest.php/boards"
```

For JSON writes:

```bash
curl -sS -X POST \
  -H "Authorization: Bearer $MYPLANNER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"New item"}' \
  "$MYPLANNER_BASE_URL/app/rest.php/boards/123/items"
```

A reusable shell helper:

```bash
mp_api() {
  method="$1"
  path="$2"
  body="${3:-}"
  if [ -n "$body" ]; then
    curl -sS -X "$method" \
      -H "Authorization: Bearer $MYPLANNER_API_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$body" \
      "$MYPLANNER_BASE_URL/app/rest.php$path"
  else
    curl -sS -X "$method" \
      -H "Authorization: Bearer $MYPLANNER_API_TOKEN" \
      "$MYPLANNER_BASE_URL/app/rest.php$path"
  fi
}
```

## Discovery Workflow

Before making changes:

1. Verify token and identity:
   ```bash
   mp_api GET /me
   ```
2. List boards:
   ```bash
   mp_api GET /boards
   ```
3. Fetch the target board shape:
   ```bash
   mp_api GET /boards/<board_id>
   ```
4. Record the exact IDs you will use:
   - `board_id`
   - `group_id`
   - `column_id`
   - `item_id`
   - `subtask_id`
5. For column writes, map by column title only after fetching the current board. Then write by numeric `column_id`.

## REST Routes

Routes are relative to `/app/rest.php`.

### Identity and metadata

```text
GET    /me
GET    /events
```

### Boards

```text
GET    /boards
POST   /boards                         {name}
GET    /boards/{id}                    board + groups + columns
PATCH  /boards/{id}                    {name}
DELETE /boards/{id}
```

### Groups

```text
GET    /boards/{id}/groups
POST   /boards/{id}/groups             {name?, color?}
PATCH  /groups/{id}                    {name?, color?, collapsed?}
DELETE /groups/{id}
```

Deleting a group deletes the group and its contained items. Confirm intent before calling `DELETE /groups/{id}`.

### Items

```text
GET    /boards/{id}/items              items including column values
GET    /boards/{id}/items/no-text      tasks/subtasks missing Text
POST   /boards/{id}/items              {name, group_id?, column_values?{columnId:value}}
GET    /items/{id}
PATCH  /items/{id}                     {name?, group_id?, column_values?}
DELETE /items/{id}
PUT    /items/{id}/values/{column_id}  {value}
```

Use `PUT /items/{id}/values/{column_id}` for a single column value. Use an empty string or `null` to clear a value.

### Subtasks

```text
GET    /items/{id}/subtasks
POST   /items/{id}/subtasks            {title}
PATCH  /subtasks/{id}                  {title?, is_done?}
DELETE /subtasks/{id}
```

Important: do not infer subtasks from names, indentation, imported labels, or visual grouping. An item is an actual MyPlanner subtask only if it is returned by `GET /items/{id}/subtasks` or addressed through `/subtasks/{id}`. Imported Monday.com data can contain regular items that appear to be subtasks but are not real subtasks.

### Updates

```text
GET    /items/{id}/updates
POST   /items/{id}/updates             {body}
DELETE /updates/{id}
```

Use updates for durable notes, progress context, and explanations of automated changes.

### Columns

```text
GET    /boards/{id}/columns
POST   /boards/{id}/columns            {title, type}
DELETE /columns/{id}
```

Column types are board-defined. Fetch columns before writing values. Treat unknown types conservatively and preserve existing values unless the user explicitly asks to change them.

### Calendar integration

```text
GET    /boards/{id}/calendar
PUT    /boards/{id}/calendar           {calendar_id, calendar_name?, date_column_id}
DELETE /boards/{id}/calendar
```

Changing calendar settings can affect external Google Calendar sync. Confirm scope before modifying these routes.

### Webhooks

```text
GET    /boards/{id}/webhooks
POST   /boards/{id}/webhooks           {url, event, config?{columnId}}
DELETE /webhooks/{id}
GET    /webhooks/{id}/deliveries
```

Webhook registration uses a challenge handshake. MyPlanner sends:

```json
{"challenge":"..."}
```

The endpoint must echo the challenge back.

Deliveries are signed with:

```text
X-Planner-Signature: sha256=HMAC_SHA256(body, secret)
```

Verify signatures before processing webhooks.

## Common Agent Tasks

### Create an item in a known group

1. Fetch board structure.
2. Find the target group ID.
3. Create the item:

```bash
mp_api POST /boards/<board_id>/items '{"name":"Call supplier","group_id":456}'
```

4. Read the item back with `GET /items/<item_id>`.

### Set a column value

1. Fetch board columns.
2. Find the exact column ID.
3. Set value:

```bash
mp_api PUT /items/<item_id>/values/<column_id> '{"value":"Done"}'
```

4. Read back `GET /items/<item_id>` and verify the value.

### Backfill missing Text

1. Call:
   ```bash
   mp_api GET /boards/<board_id>/items/no-text
   ```
2. Review each candidate.
3. Write one item at a time with explicit user-approved text.
4. Verify the item no longer appears in `/items/no-text`.

### Sync or repair Monday.com imports

When cleaning Monday.com imports, never rely on display shape alone.

Recommended flow:

1. Fetch all board items.
2. For each possible parent item, fetch `GET /items/{id}/subtasks`.
3. Build a map of actual subtask relationships from the subtask endpoint only.
4. Treat items that merely look nested as normal items until converted or linked by an explicit MyPlanner operation.
5. Preserve names, statuses, dates, and updates when converting structure.
6. After repair, verify with both board items and subtask endpoint reads.

### Register a webhook

1. Build an HTTPS endpoint that echoes registration challenges.
2. Verify `X-Planner-Signature` on deliveries.
3. Register:

```bash
mp_api POST /boards/<board_id>/webhooks '{"url":"https://example.com/myplanner-hook","event":"item.updated"}'
```

4. Read back webhooks and deliveries:

```bash
mp_api GET /boards/<board_id>/webhooks
mp_api GET /webhooks/<webhook_id>/deliveries
```

## Safety Rules

- Never log API tokens.
- Never commit API tokens into a repository.
- Confirm before deleting boards, groups, items, columns, webhooks, or calendar integrations.
- Read before write: fetch the current object and board shape before mutating.
- Write by IDs, not by guessed names.
- After every write, read back the object and verify the expected field changed.
- Use updates to leave an audit note when an agent performs a meaningful automated change.
- For sync jobs, make operations idempotent. Store remote IDs or stable matching keys outside task names when possible.
- For imported Monday data, distinguish actual subtasks from regular items that only appear nested.

## Troubleshooting

### 401 Missing or invalid API token

- Check `MYPLANNER_API_TOKEN` is set.
- Recreate the token in MyPlanner `Integrate` > `API tokens`.
- Confirm the request includes a Bearer authorization header.

### 404 No route

- Confirm the path is under `/app/rest.php`.
- Try the fallback format: `/app/rest.php?path=/boards`.

### Board, item, or group not found

- Verify the token belongs to the user who owns the board.
- Re-list boards and fetch current board structure.
- IDs may differ across boards or environments.

### Column write did not do what you expected

- Fetch `GET /boards/{id}/columns`.
- Confirm the target `column_id`, title, and type.
- Read the item back and inspect `column_values`.

## Verification Checklist

- [ ] Token authenticated with `GET /me`.
- [ ] Target board was discovered with `GET /boards` and `GET /boards/{id}`.
- [ ] Numeric IDs were used for writes.
- [ ] Destructive operations were explicitly confirmed.
- [ ] Writes were verified with read-back calls.
- [ ] Subtask operations used `/items/{id}/subtasks` or `/subtasks/{id}`, not visual inference.
- [ ] Webhook endpoints echoed challenges and verified `X-Planner-Signature`.
