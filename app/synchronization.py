"""Shared-state correctness (Section 11.5). Software locks - NOT hardware cache coherence."""
import threading, time


class TicketStore:
    def __init__(self, tickets):
        self._tickets = {t.ticket_id: t for t in tickets}
        self._lock = threading.Lock()
        self.claim_log = []                    # (ticket_id, worker) for every successful claim

    def claim(self, ticket_id, worker):
        """Atomically claim a ticket. Exactly one caller can win."""
        with self._lock:
            t = self._tickets[ticket_id]
            if t.status != "QUEUED":
                return False
            t.status, t.assigned_worker, t.started_at = "IN_PROGRESS", worker, time.time()
            self.claim_log.append((ticket_id, worker))
            return True

    def complete(self, ticket_id):
        with self._lock:
            t = self._tickets[ticket_id]
            t.status, t.processed_at = "RESOLVED", time.time()

    def add(self, ticket):
        with self._lock:
            self._tickets[ticket.ticket_id] = ticket

    def remove(self, ticket_id):
        with self._lock:
            self._tickets.pop(ticket_id, None)

    def mark_queued(self, ticket_id):
        with self._lock:
            self._tickets[ticket_id].status = "QUEUED"

    def snapshot(self):
        with self._lock:
            return list(self._tickets.values())
