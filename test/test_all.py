import copy, json, queue, threading, unittest
from app.ticket_model import Ticket, load_tickets
from app.classification import classify
from app.prioritisation import prioritise
from app.queue_manager import BoundedTicketQueue
from app.synchronization import TicketStore
from app.processor import run_sequential
from app.parallel_processor import run_parallel
from app.main import prepare, DEFAULT


class Tests(unittest.TestCase):
    def test_creation(self):
        t = Ticket("T1", "E1", "VPN down", "high")
        self.assertEqual((t.status, t.category, t.priority), ("NEW", None, None))

    def test_classification_accuracy(self):
        truth = {r["ticket_id"]: r["true_category"] for r in json.load(open(DEFAULT))}
        tickets = [classify(t) for t in load_tickets(DEFAULT)]
        acc = sum(t.category == truth[t.ticket_id] for t in tickets) / len(tickets)
        self.assertGreaterEqual(acc, 0.98)

    def test_prioritisation_order(self):
        a = prioritise(classify(Ticket("A", "E", "Printer jam", "critical")))
        b = prioritise(classify(Ticket("B", "E", "Parking sticker renewal", "low")))
        self.assertGreater(a.priority, b.priority)

    def test_queue_order_and_bound(self):
        q = BoundedTicketQueue(2)
        lo = prioritise(classify(Ticket("L", "E", "Parking sticker", "low")))
        hi = prioritise(classify(Ticket("H", "E", "VPN down", "critical")))
        q.put(lo); q.put(hi)
        with self.assertRaises(queue.Full):
            q.put(hi, timeout=0.05)
        self.assertEqual(q.get().ticket_id, "H")

    def test_only_one_claim_wins(self):
        t = Ticket("X", "E", "VPN", "low"); t.status = "QUEUED"
        store, wins = TicketStore([t]), []
        ths = [threading.Thread(target=lambda i=i: wins.append(store.claim("X", f"W{i}"))) for i in range(50)]
        [th.start() for th in ths]; [th.join() for th in ths]
        self.assertEqual(sum(wins), 1)

    def test_parallel_correct_and_faster(self):
        tickets = prepare(DEFAULT)[:60]
        seq, _ = run_sequential(copy.deepcopy(tickets))
        par, store = run_parallel(copy.deepcopy(tickets), workers=4, queue_size=10)
        self.assertEqual(par.processed, 60)
        self.assertEqual(par.duplicates, 0)
        self.assertTrue(all(t.status == "RESOLVED" for t in store.snapshot()))
        self.assertGreater(seq.elapsed / par.elapsed, 1.2)


if __name__ == "__main__":
    unittest.main()
