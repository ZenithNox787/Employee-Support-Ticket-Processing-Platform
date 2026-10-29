"""Stage 3: rule-based classification using logical conditions (Unit 2 idea)."""
KEYWORDS = {
    "Access": ["permission", "admin rights", "grant access", "access to", "role change"],
    "Hardware": ["laptop", "printer", "monitor", "keyboard", "mouse", "battery"],
    "HR": ["payslip", "leave", "salary", "insurance", "benefits", "bank details"],
    "Administration": ["desk", "parking", "id card", "conference room", "stationery"],
    "IT": ["vpn", "outlook", "email", "software", "wifi", "login", "erp", "install"],
}


def classify(ticket):
    text = ticket.description.lower()
    scores = {cat: sum(k in text for k in kws) for cat, kws in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    ticket.category = best if scores[best] > 0 else "General"
    ticket.status = "CLASSIFIED"
    return ticket
