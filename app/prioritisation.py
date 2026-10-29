"""Stage 4: numeric priority score. Higher score = processed first."""
URGENCY_WEIGHT = {"low": 1, "medium": 2, "high": 3, "critical": 4}
CATEGORY_WEIGHT = {"Access": 3, "IT": 2, "Hardware": 2, "HR": 1, "Administration": 0, "General": 0}


def prioritise(ticket):
    ticket.priority = URGENCY_WEIGHT[ticket.urgency] * 10 + CATEGORY_WEIGHT.get(ticket.category, 0)
    return ticket
