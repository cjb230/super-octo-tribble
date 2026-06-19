from patchwork.services.cache_box import LAST_RESULTS, TICKET_ORDER
from patchwork.utils.date_tools import now_stamp


def remember_result(result_doc):
    ticket = result_doc.get("input", {}).get("meta", {}).get("ticket", "UNKNOWN")
    wrapper = {
        "stored_at": now_stamp(),
        "payload": result_doc,
    }
    LAST_RESULTS[ticket] = wrapper
    if ticket not in TICKET_ORDER:
        TICKET_ORDER.append(ticket)
    return wrapper


def get_last_for_ticket(ticket):
    item = LAST_RESULTS.get(ticket)
    if item:
        return item
    return None


def known_tickets():
    return list(TICKET_ORDER)
