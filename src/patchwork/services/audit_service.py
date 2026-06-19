from patchwork.services.cache_box import LAST_RESULTS, TICKET_ORDER
from patchwork.db.repository import get_latest_ticket_run, list_known_tickets, save_transform_result
from patchwork.utils.date_tools import now_stamp


def remember_result(result_doc, endpoint_name="transform"):
    ticket = result_doc.get("input", {}).get("meta", {}).get("ticket", "UNKNOWN")
    stored = save_transform_result(endpoint_name, result_doc)
    wrapper = {
        "stored_at": stored.get("stored_at", now_stamp()),
        "payload": result_doc,
        "run_id": stored.get("run_id"),
    }
    LAST_RESULTS[ticket] = wrapper
    if ticket not in TICKET_ORDER:
        TICKET_ORDER.append(ticket)
    return wrapper


def get_last_for_ticket(ticket):
    item = LAST_RESULTS.get(ticket)
    if item:
        return item
    item = get_latest_ticket_run(ticket)
    if item:
        LAST_RESULTS[ticket] = item
        if ticket not in TICKET_ORDER:
            TICKET_ORDER.append(ticket)
        return item
    return None


def known_tickets():
    tickets = list_known_tickets()
    if tickets:
        return tickets
    return list(TICKET_ORDER)
