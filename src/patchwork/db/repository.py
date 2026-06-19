from patchwork.db.connection import get_connection
from patchwork.db.schema import initialize_database
from patchwork.utils.date_tools import now_stamp


def save_transform_result(endpoint_name, result_doc):
    initialize_database()
    input_doc = result_doc.get("input", {})
    meta = input_doc.get("meta", {})
    facts = input_doc.get("facts", {})
    words = input_doc.get("words", {})
    meaning = result_doc.get("meaning", {})
    flags = result_doc.get("flags", {})
    stored_at = now_stamp()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO transform_runs (
                created_at, endpoint_name, ticket, source, region, region_code,
                amount, retry_value, vip_value, tone, topic, raw_text, shifted_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stored_at,
                endpoint_name,
                meta.get("ticket", "UNKNOWN"),
                meta.get("source", "unknown"),
                meta.get("region", "middle"),
                meta.get("region_code", "UNK"),
                facts.get("amount", 0),
                facts.get("retry", "no"),
                facts.get("vip", "no"),
                words.get("tone", ""),
                words.get("topic", ""),
                words.get("raw", ""),
                meaning.get("shifted_text", ""),
            ),
        )
        run_id = cursor.lastrowid
        conn.execute(
            """
            INSERT INTO run_flags (run_id, decision_flag, send_partner_copy, manual_review)
            VALUES (?, ?, ?, ?)
            """,
            (
                run_id,
                flags.get("decision_flag", "STANDARD_PIPE"),
                1 if flags.get("send_partner_copy") else 0,
                1 if flags.get("manual_review") else 0,
            ),
        )
        conn.executemany(
            """
            INSERT INTO word_swaps (run_id, swap_index, from_word, to_word)
            VALUES (?, ?, ?, ?)
            """,
            [
                (run_id, index, row.get("from", ""), row.get("to", ""))
                for index, row in enumerate(meaning.get("word_swaps", []), start=1)
            ],
        )
        conn.executemany(
            """
            INSERT INTO trail_steps (run_id, trail_index, ticket_value)
            VALUES (?, ?, ?)
            """,
            [
                (run_id, index, ticket_value)
                for index, ticket_value in enumerate(meaning.get("trail_snapshot", []), start=1)
            ],
        )
        conn.commit()
    return {"run_id": run_id, "stored_at": stored_at}


def record_api_call(method, path, status_code, duration_ms, remote_addr="", ticket=None, run_id=None):
    initialize_database()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO api_calls (called_at, method, path, status_code, duration_ms, remote_addr, ticket, run_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (now_stamp(), method, path, status_code, duration_ms, remote_addr or "", ticket, run_id),
        )
        conn.commit()


def get_latest_ticket_run(ticket):
    initialize_database()
    with get_connection() as conn:
        run = conn.execute(
            """
            SELECT id, created_at, endpoint_name, ticket, source, region, region_code,
                   amount, retry_value, vip_value, tone, topic, raw_text, shifted_text
            FROM transform_runs
            WHERE ticket = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (ticket,),
        ).fetchone()
        if run is None:
            return None
        flag = conn.execute(
            """
            SELECT decision_flag, send_partner_copy, manual_review
            FROM run_flags
            WHERE run_id = ?
            """,
            (run["id"],),
        ).fetchone()
        swaps = conn.execute(
            """
            SELECT from_word, to_word
            FROM word_swaps
            WHERE run_id = ?
            ORDER BY swap_index
            """,
            (run["id"],),
        ).fetchall()
        trail = conn.execute(
            """
            SELECT ticket_value
            FROM trail_steps
            WHERE run_id = ?
            ORDER BY trail_index
            """,
            (run["id"],),
        ).fetchall()

    payload = {
        "input": {
            "meta": {
                "ticket": run["ticket"],
                "source": run["source"],
                "region": run["region"],
                "region_code": run["region_code"],
            },
            "facts": {
                "amount": run["amount"],
                "retry": run["retry_value"],
                "vip": run["vip_value"],
            },
            "words": {
                "raw": run["raw_text"],
                "tone": run["tone"],
                "topic": run["topic"],
            },
            "raw_text": run["raw_text"],
        },
        "meaning": {
            "ticket": run["ticket"],
            "meta": {
                "ticket": run["ticket"],
                "source": run["source"],
                "region": run["region"],
                "region_code": run["region_code"],
            },
            "facts": {
                "amount": run["amount"],
                "retry": run["retry_value"],
                "vip": run["vip_value"],
            },
            "raw_text": run["raw_text"],
            "shifted_text": run["shifted_text"],
            "word_swaps": [{"from": row["from_word"], "to": row["to_word"]} for row in swaps],
            "trail_snapshot": [row["ticket_value"] for row in trail],
        },
        "flags": {
            "decision_flag": flag["decision_flag"],
            "send_partner_copy": bool(flag["send_partner_copy"]),
            "manual_review": bool(flag["manual_review"]),
        },
    }
    return {"stored_at": run["created_at"], "payload": payload, "run_id": run["id"]}


def list_known_tickets():
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT ticket, MAX(created_at) AS latest_seen
            FROM transform_runs
            GROUP BY ticket
            ORDER BY latest_seen DESC
            """
        ).fetchall()
    return [row["ticket"] for row in rows]


def count_api_calls():
    initialize_database()
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS total_calls FROM api_calls").fetchone()
    return row["total_calls"]


def reset_everything():
    initialize_database()
    with get_connection() as conn:
        conn.execute("DELETE FROM api_calls")
        conn.execute("DELETE FROM trail_steps")
        conn.execute("DELETE FROM word_swaps")
        conn.execute("DELETE FROM run_flags")
        conn.execute("DELETE FROM transform_runs")
        conn.commit()
