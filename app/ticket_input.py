"""Stage 1: ticket input. Generates the simulated dataset (no real employee data)."""
import json, random, sys, os

TEMPLATES = {
    "IT": ["VPN keeps disconnecting when working from home",
           "Outlook email is not syncing on my phone",
           "Need software installed: Python and VS Code",
           "Wifi is very slow on the third floor",
           "Unable to login to the ERP portal after the update"],
    "Hardware": ["Laptop battery drains within an hour",
                 "Printer on floor 2 shows a paper jam",
                 "Monitor flickers and goes black",
                 "Keyboard keys are not responding"],
    "Access": ["Request permission to view the finance shared folder",
               "Need admin rights on my workstation",
               "Role change: please grant access to the HR dashboard",
               "Access to the server rack is denied"],
    "HR": ["Payslip for last month is missing",
           "Question about my leave balance",
           "Update bank details for salary credit",
           "Query on health insurance benefits policy"],
    "Administration": ["Request a new desk near my team",
                       "Parking sticker renewal",
                       "ID card lost, need a replacement",
                       "Book conference room for a client visit",
                       "Stationery supply is running out"],
}
URGENCIES = ["low", "medium", "high", "critical"]
URGENCY_WEIGHTS = [40, 35, 18, 7]


def generate_dataset(n=200, seed=42):
    rng = random.Random(seed)
    out = []
    for i in range(1, n + 1):
        cat = rng.choice(list(TEMPLATES))
        out.append({
            "ticket_id": f"TKT-{i:04d}",
            "employee_id": f"EMP-{rng.randint(1, 60):03d}",
            "description": rng.choice(TEMPLATES[cat]),
            "urgency": rng.choices(URGENCIES, URGENCY_WEIGHTS)[0],
            "true_category": cat,      # ground truth, used only to test classification
        })
    return out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_tickets.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(generate_dataset(n), f, indent=2)
    print(f"Wrote {n} simulated tickets to {os.path.normpath(path)}")
