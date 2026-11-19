# Steal a Brainrot API

A FastAPI service that tracks **Steal a Brainrot** (Roblox tycoon by SpyderSammy) game data in a
SQLite database: brainrots, rarities, mutations, traits, game updates (changelog) and live events.

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m app.seed        # create/seed brainrot.db (add --reset to wipe first)
.venv/bin/uvicorn app.main:app --port 8000
```

Interactive docs: http://localhost:8000/docs

Admin write endpoints require the `X-API-Key` header. Set `ADMIN_API_KEY` in the environment
(default dev key is `change-me-dev-key` — change it before exposing anything).

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Service health |
| GET | `/brainrots` | List/search brainrots. Filters: `q`, `rarity`, `event`, `limited`, `added_in_update`, `sort`, `order`, `limit`, `offset` |
| GET | `/brainrots/{slug}` | One brainrot by slug or name |
| POST/PUT/DELETE | `/brainrots` | Admin CRUD (new Saturday updates add new brainrots here) |
| GET | `/mutations` | All mutations with income multipliers. Filter: `permanent` |
| POST | `/mutations` | Admin add mutation |
| GET/POST | `/traits` | List/add traits |
| GET | `/updates` | Changelog feed, newest first (`limit`) |
| GET | `/updates/latest` | Most recent update |
| GET | `/updates/{version}` | One update |
| POST | `/updates` | Admin log a new game update (version, title, body, new_brainrots, new_mutations, released_at ISO 8601) |
| GET | `/events` | Tracked events. Filter: `active` |
| GET | `/events/active-now` | Events whose start/end window contains now |
| POST | `/events` | Admin schedule an event |
| GET | `/calculator` | `?brainrot=<slug>&mutation=<name>&traits=<a,b>` → computed income/s |

Data is seeded from community guides. `income` values are editable via the admin endpoints —
log every Saturday update through `POST /updates` and it becomes the changelog feed.
