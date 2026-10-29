"""Ticket record (Section 12.2 of the report)."""
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

STATUSES = ("NEW", "CLASSIFIED", "QUEUED", "IN_PROGRESS", "RESOLVED")


@dataclass
class Ticket:
    ticket_id: str
    employee_id: str
    description: str
    urgency: str                       # low | medium | high | critical
    category: Optional[str] = None
    priority: Optional[int] = None
    status: str = "NEW"
    created_at: float = field(default_factory=time.time)
    queued_at: Optional[float] = None
    started_at: Optional[float] = None
    assigned_worker: Optional[str] = None
    processed_at: Optional[float] = None

    def to_dict(self):
        return asdict(self)


def load_tickets(path):
    """Load raw tickets from JSON (extra keys such as true_category are ignored)."""
    import json
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    keys = ("ticket_id", "employee_id", "description", "urgency")
    return [Ticket(**{k: r[k] for k in keys}) for r in raw]
