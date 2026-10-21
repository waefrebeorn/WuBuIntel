#!/usr/bin/env python3
"""wbi1_triage.py — the Bureau's WBI-1 triage helper (GOV-11).

Wraps WuBuCore's `vigilance` tool for ledger use. Reads a report
from the command line and emits a ledger-ready row:

    wbi1_triage.py CLASS SEVERITY NAMES_OFFICIAL CAPACITY SPIKE_Z

Classes (match vigilance.h):
    0 power concentration, 1 rule asymmetry, 2 fear-lie,
    3 above-license, 4 penny evasion, 5 other
"""
import subprocess
import sys
from datetime import date

CLASS_LABELS = {
    0: "POWER CONCENTRATION",
    1: "RULE ASYMMETRY",
    2: "FEAR LIE",
    3: "ABOVE LICENSE",
    4: "PENNY EVASION",
    5: "OTHER",
}


def main() -> int:
    if len(sys.argv) != 6:
        print(__doc__)
        return 2
    cls, sev, names, cap, z = sys.argv[1:6]
    try:
        out = subprocess.run(
            ["bin/vigilance", cls, sev, names, cap, z],
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        print("ERROR: bin/vigilance not built (run make in WuBuCore)")
        return 1
    if out.returncode != 0:
        print(out.stderr or "ERROR: triage failed")
        return 2

    # Parse the tool's output into a ledger row
    priority = escalate = ""
    for line in out.stdout.splitlines():
        if "priority" in line:
            priority = line.split(":", 1)[1].strip().split("/")[0]
        if "escalate" in line and ":" in line:
            escalate = line.split(":", 1)[1].strip().split(" ")[0]

    # Ledger row: WBI-RRRR,date,class,severity,priority,escalation
    print(f"WBI-{date.today().strftime('%Y%m%d')}-NEW,"
          f"{date.today().isoformat()},"
          f"{CLASS_LABELS.get(int(cls), 'OTHER')},"
          f"{sev},{priority},{escalate}")
    print(out.stdout, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
