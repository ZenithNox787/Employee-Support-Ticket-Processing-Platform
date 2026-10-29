"""Stages 6-8: processing, sequential baseline, and metrics."""
import time
from dataclasses import dataclass
from .synchronization import TicketStore

# Simulated service time per category (seconds). time.sleep models I/O-style waiting
# (looking up records, calling other systems). See README for why.
SERVICE_TIME = {"IT": 0.008, "Hardware": 0.010, "Access": 0.006,
                "HR": 0.005, "Administration": 0.004, "General": 0.005}


def simulate_work(ticket, scale=1.0):
    time.sleep(SERVICE_TIME.get(ticket.category, 0.005) * scale)


@dataclass
class RunResult:
    mode: str
    workers: int
    elapsed: float
    processed: int
    duplicates: int
    avg_wait: float

    @property
    def throughput(self):
        return self.processed / self.elapsed if self.elapsed else 0.0


def build_result(mode, workers, elapsed, store, total):
    tickets = store.snapshot()
    done = [t for t in tickets if t.status == "RESOLVED"]
    ids = [c[0] for c in store.claim_log]
    waits = [t.started_at - t.queued_at for t in done if t.started_at and t.queued_at]
    return RunResult(mode, workers, elapsed, len(done), len(ids) - len(set(ids)),
                     sum(waits) / len(waits) if waits else 0.0)


def run_sequential(tickets, work=simulate_work):
    store = TicketStore(tickets)
    for t in tickets:
        store.mark_queued(t.ticket_id); t.queued_at = time.time()
    start = time.perf_counter()
    for t in sorted(tickets, key=lambda x: -x.priority):
        if store.claim(t.ticket_id, "seq"):
            work(t)
            store.complete(t.ticket_id)
    return build_result("sequential", 1, time.perf_counter() - start, store, len(tickets)), store
