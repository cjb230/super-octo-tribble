# patched-flow-demo

Demo service for showing Copilot-driven bug fixes and feature work.

This service accepts odd text blocks that look like this:

```text
META:: ticket=>A-100 ;; source=>fax ;; region=>north
WORDS:: raw=>customer says package late and needs rapid lane ;; tone=>angry
FACTS:: amount=>1450 ;; retry=>yes ;; vip=>no
```

It turns them into JSON after doing a bit of meaning-shifting through Datamuse, with a small built-in fallback word list when the external lookup is unavailable.

The runtime is FastAPI. The service writes call logs and transform records into a local SQLite database.

## Run

```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_server.py
```

## Endpoints

- `GET /`
- `GET /api/v1/health`
- `POST /api/v1/transform`
- `POST /api/v1/flag-only`
- `GET /api/v1/examples/basic`
- `GET /api/v1/admin/ping`
- `POST /api/v1/admin/replay`

## Example

```bash
curl -s http://127.0.0.1:5001/api/v1/transform \
  -H 'content-type: application/json' \
  -d '{"raw_text":"META:: ticket=>A-100 ;; source=>fax ;; region=>north\nWORDS:: raw=>customer says package late and needs rapid lane ;; tone=>angry\nFACTS:: amount=>1450 ;; retry=>yes ;; vip=>no"}' | jq
```

The `jq` pipe is optional; remove it if `jq` is not installed.

The default database file lands at `var/patchwork.sqlite3`.

To populate it with demo traffic:

```bash
sqlite3 var/patchwork.sqlite3 < scripts/seed_data.sql
```
