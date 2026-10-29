"""Live ticket platform: raise tickets from a web form; background workers process them.
Run:  python3 -m app.server [--workers 4] [--queue-size 20] [--port 8000] [--speed 100]
Then open http://localhost:8000
"""
import argparse, json, os, queue, random, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .ticket_model import Ticket
from .classification import classify
from .prioritisation import prioritise, URGENCY_WEIGHT
from .queue_manager import BoundedTicketQueue
from .synchronization import TicketStore
from .processor import simulate_work
from .ticket_input import generate_dataset

FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")


class TicketService:
    def __init__(self, workers=4, queue_size=20, speed=100):
        self.workers, self.queue_size, self.speed = workers, queue_size, speed
        self.store = TicketStore([])
        self.q = BoundedTicketQueue(queue_size)
        self._lock, self._n = threading.Lock(), 0
        for i in range(workers):
            threading.Thread(target=self._worker, args=(f"W{i+1}",), daemon=True).start()

    def _worker(self, name):
        while True:
            t = self.q.get()
            if t is not None and self.store.claim(t.ticket_id, name):
                simulate_work(t, self.speed)          # slowed down so progress is visible in the UI
                self.store.complete(t.ticket_id)

    def raise_ticket(self, employee_id, description, urgency):
        description = (description or "").strip()[:300]
        employee_id = (employee_id or "").strip()[:30] or "EMP-000"
        if not description:
            raise ValueError("Description is required")
        if urgency not in URGENCY_WEIGHT:
            raise ValueError("Urgency must be one of: " + ", ".join(URGENCY_WEIGHT))
        with self._lock:
            self._n += 1
            tid = f"TKT-{self._n:04d}"
        t = prioritise(classify(Ticket(tid, employee_id, description, urgency)))
        self.store.add(t)
        try:
            self.q.put(t, timeout=0.2)                # bounded queue: rejects when full
        except queue.Full:
            self.store.remove(tid)
            raise
        return t

    def snapshot(self):
        tickets = sorted(self.store.snapshot(), key=lambda t: t.ticket_id, reverse=True)
        counts = {}
        for t in tickets:
            counts[t.status] = counts.get(t.status, 0) + 1
        return {"tickets": [t.to_dict() for t in tickets], "counts": counts,
                "workers": self.workers, "queue_size": self.q.size(), "queue_capacity": self.queue_size}


def make_handler(service):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _json_body(self):
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")

        def do_GET(self):
            if self.path == "/api/tickets":
                self._send(200, service.snapshot())
            elif self.path in ("/", "/index.html"):
                with open(FRONTEND, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self):
            try:
                body = self._json_body()
                if self.path == "/api/tickets":
                    t = service.raise_ticket(body.get("employee_id"), body.get("description"), body.get("urgency"))
                    self._send(201, t.to_dict())
                elif self.path == "/api/sample":
                    accepted = 0
                    for r in generate_dataset(int(body.get("count", 20)), seed=random.randint(0, 10**6)):
                        try:
                            service.raise_ticket(r["employee_id"], r["description"], r["urgency"])
                            accepted += 1
                        except queue.Full:
                            break
                    self._send(200, {"accepted": accepted})
                else:
                    self._send(404, {"error": "not found"})
            except queue.Full:
                self._send(503, {"error": "Queue is full - try again in a moment"})
            except (ValueError, json.JSONDecodeError) as e:
                self._send(400, {"error": str(e)})

        def log_message(self, *a):
            pass
    return Handler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--queue-size", type=int, default=20)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--speed", type=float, default=100, help="multiplier on simulated work time")
    a = ap.parse_args()
    svc = TicketService(a.workers, a.queue_size, a.speed)
    print(f"Open http://localhost:{a.port}  (workers={a.workers}, queue={a.queue_size}). Ctrl+C to stop.")
    ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(svc)).serve_forever()


if __name__ == "__main__":
    main()
