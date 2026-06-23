seed_data.sql populates the SQLite database with a couple of weeks of light demo traffic.

Example:
python - <<'PY'
import sqlite3
from pathlib import Path

db = Path("var/patchwork.sqlite3")
sql = Path("scripts/seed_light_usage.sql").read_text()
conn = sqlite3.connect(db)
conn.executescript(sql)
conn.close()
PY
