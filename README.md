# Employee Support Ticket Processing Platform (CCSEO304, Group 7)

Prototype of: Ticket Input -> Storage -> Classification -> Prioritisation -> Queue -> Processing -> Status Update.

## Run (Python 3.8+, no external packages)
    python3 -m app.server              # live app: raise tickets at http://localhost:8000
    python -m app.ticket_input 200     # regenerate data/sample_tickets.json (seeded, simulated data)
    python -m app.main --workers 4 --queue-size 20
    python -m unittest discover -s tests -v

## What maps to the report
| Report concept | Code |
|---|---|
| Ticket record (12.2) | app/ticket_model.py |
| Logic conditions (Unit 2) | classification.py, prioritisation.py |
| Bounded queue / flow control (11.6 analogy) | queue_manager.py |
| Shared-state correctness, locks (11.5) | synchronization.py (TicketStore.claim) |
| Point-to-point sync | threading.Event: reporter waits for workers |
| Barrier sync | threading.Barrier: workers finish the batch together |
| Ticket submission UI + live workers | app/server.py, frontend/index.html |
| Sequential vs parallel, speedup (12.4) | processor.py, parallel_processor.py, main.py |

## Honest limitations (keep these in your report)
- Processing time is simulated with time.sleep (I/O-style waiting). Python threads do not speed up
  CPU-bound work because of the GIL, so describe the evaluation as a simulated I/O-bound workload.
- Locks/queues are software coordination, not hardware cache coherence, LL-SC or interconnects.
- Stages run as ordered steps and do not overlap, so this is not a hardware-style pipeline.
- Priority ordering applies within the queue's capacity window because the producer feeds it gradually.
- Timings vary per machine. Report your own measured numbers.
