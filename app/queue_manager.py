"""Stage 5: bounded priority queue (flow control, Section 11.6 analogy)."""
import itertools, queue, time


class BoundedTicketQueue:
    def __init__(self, capacity=20):
        self._q = queue.PriorityQueue(maxsize=capacity)
        self._seq = itertools.count()          # tie-breaker keeps FIFO within equal priority

    def put(self, ticket, timeout=None):
        ticket.status = "QUEUED"
        ticket.queued_at = time.time()
        self._q.put((-ticket.priority, next(self._seq), ticket), timeout=timeout)  # blocks when full

    def put_sentinel(self):
        self._q.put((1, next(self._seq), None))   # sorts after every real ticket

    def get(self):
        return self._q.get()[2]

    def size(self):
        return self._q.qsize()
