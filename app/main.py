"""Run:  python -m app.main [--workers 4] [--queue-size 20] [--data data/sample_tickets.json]"""
import argparse, copy, os
from .ticket_model import load_tickets
from .classification import classify
from .prioritisation import prioritise
from .processor import run_sequential
from .parallel_processor import run_parallel

DEFAULT = os.path.join(os.path.dirname(__file__), "..", "data", "sample_tickets.json")


def prepare(path):
    return [prioritise(classify(t)) for t in load_tickets(path)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--queue-size", type=int, default=20)
    a = ap.parse_args()

    tickets = prepare(a.data)
    cats = {}
    for t in tickets:
        cats[t.category] = cats.get(t.category, 0) + 1
    print(f"Loaded {len(tickets)} tickets | categories: {cats}")
    top = sorted(tickets, key=lambda t: -t.priority)[:3]
    print("Top priority:", [(t.ticket_id, t.category, t.urgency, t.priority) for t in top])

    seq, _ = run_sequential(copy.deepcopy(tickets))
    par, store = run_parallel(copy.deepcopy(tickets), a.workers, a.queue_size)

    print(f"\n{'Mode':<11}{'Workers':>8}{'Time(s)':>10}{'Tickets/s':>11}{'Resolved':>9}{'Dupes':>6}{'AvgWait(s)':>11}")
    for r in (seq, par):
        print(f"{r.mode:<11}{r.workers:>8}{r.elapsed:>10.3f}{r.throughput:>11.1f}{r.processed:>9}{r.duplicates:>6}{r.avg_wait:>11.3f}")
    speedup = seq.elapsed / par.elapsed
    print(f"\nSpeedup = Ts/Tp = {seq.elapsed:.3f}/{par.elapsed:.3f} = {speedup:.2f}x "
          f"(efficiency {speedup / a.workers:.0%})")
    per = {}
    for _, w in store.claim_log:
        per[w] = per.get(w, 0) + 1
    print("Tickets per worker:", dict(sorted(per.items())))
    ok = par.processed == len(tickets) and par.duplicates == 0
    print("Correctness check:", "PASS (no loss, no duplicates)" if ok else "FAIL")


if __name__ == "__main__":
    main()
