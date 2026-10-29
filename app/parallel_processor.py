"""Concurrent processing: producer + N workers, bounded queue, barrier, event signalling."""
import threading, time
from .processor import simulate_work, build_result
from .queue_manager import BoundedTicketQueue
from .synchronization import TicketStore


def run_parallel(tickets, workers=4, queue_size=20, work=simulate_work):
    store = TicketStore(tickets)
    q = BoundedTicketQueue(queue_size)
    batch_done = threading.Event()                          # point-to-point signal
    barrier = threading.Barrier(workers, action=batch_done.set)   # barrier sync
    report = {}

    def producer():
        for t in tickets:
            store.mark_queued(t.ticket_id)
            q.put(t)                                        # blocks if queue is full
        for _ in range(workers):
            q.put_sentinel()

    def worker(name):
        while True:
            t = q.get()
            if t is None:
                break
            if store.claim(t.ticket_id, name):              # lock-protected claim
                work(t)
                store.complete(t.ticket_id)
        barrier.wait()                                      # wait for the whole batch

    def reporter():
        batch_done.wait()                                   # notified when all workers finish
        report["resolved"] = sum(t.status == "RESOLVED" for t in store.snapshot())

    threads = [threading.Thread(target=producer), threading.Thread(target=reporter)]
    threads += [threading.Thread(target=worker, args=(f"W{i+1}",)) for i in range(workers)]
    start = time.perf_counter()
    for th in threads: th.start()
    for th in threads: th.join()
    elapsed = time.perf_counter() - start
    return build_result("parallel", workers, elapsed, store, len(tickets)), store
