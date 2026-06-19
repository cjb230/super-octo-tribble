LAST_RESULTS = {}
TICKET_ORDER = []


def clear_everything():
    LAST_RESULTS.clear()
    TICKET_ORDER[:] = []
    return True


def maybe_get(ticket):
    if ticket in LAST_RESULTS:
        return LAST_RESULTS[ticket]
    return None
