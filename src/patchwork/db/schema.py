from patchwork.db.connection import get_connection


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS transform_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        endpoint_name TEXT NOT NULL,
        ticket TEXT NOT NULL,
        source TEXT NOT NULL,
        region TEXT NOT NULL,
        region_code TEXT NOT NULL,
        amount REAL NOT NULL,
        retry_value TEXT NOT NULL,
        vip_value TEXT NOT NULL,
        tone TEXT NOT NULL,
        topic TEXT NOT NULL,
        raw_text TEXT NOT NULL,
        shifted_text TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS run_flags (
        run_id INTEGER PRIMARY KEY,
        decision_flag TEXT NOT NULL,
        send_partner_copy INTEGER NOT NULL CHECK (send_partner_copy IN (0, 1)),
        manual_review INTEGER NOT NULL CHECK (manual_review IN (0, 1)),
        FOREIGN KEY (run_id) REFERENCES transform_runs(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS word_swaps (
        run_id INTEGER NOT NULL,
        swap_index INTEGER NOT NULL,
        from_word TEXT NOT NULL,
        to_word TEXT NOT NULL,
        PRIMARY KEY (run_id, swap_index),
        FOREIGN KEY (run_id) REFERENCES transform_runs(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trail_steps (
        run_id INTEGER NOT NULL,
        trail_index INTEGER NOT NULL,
        ticket_value TEXT NOT NULL,
        PRIMARY KEY (run_id, trail_index),
        FOREIGN KEY (run_id) REFERENCES transform_runs(id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS api_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        called_at TEXT NOT NULL,
        method TEXT NOT NULL,
        path TEXT NOT NULL,
        status_code INTEGER NOT NULL,
        duration_ms INTEGER NOT NULL CHECK (duration_ms >= 0),
        remote_addr TEXT NOT NULL,
        ticket TEXT,
        run_id INTEGER,
        FOREIGN KEY (run_id) REFERENCES transform_runs(id) ON DELETE SET NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_transform_runs_ticket_created ON transform_runs(ticket, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_api_calls_called_at ON api_calls(called_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_api_calls_path ON api_calls(path, called_at DESC)",
]


def initialize_database():
    with get_connection() as conn:
        for statement in SCHEMA_STATEMENTS:
            conn.execute(statement)
        conn.commit()
