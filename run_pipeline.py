import subprocess
import sys
import time
import os
from datetime import datetime

# ── Force UTF-8 output so Unicode box chars / emoji work on Windows too ────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ── CRITICAL: switch working directory to this script's own folder ─────────────
# Ensures scripts and outputs/ are always found no matter where you launch from
# e.g.  python WaterBlockchainProject/run_pipeline.py   ← works from any dir
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
os.makedirs("outputs", exist_ok=True)

# ── UTF-8 environment passed to every subprocess ──────────────────────────────
UTF8_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

# ── Pipeline stages ───────────────────────────────────────────────────────────
PIPELINE = [
    {
        "step":    1,
        "script":  "generate_data.py",
        "label":   "Data generated",
        "desc":    "Generating 50 rows of water sensor data → outputs/water_data.csv",
    },
    {
        "step":    2,
        "script":  "detect_anomalies.py",
        "label":   "Anomalies detected",
        "desc":    "Checking WHO standards → outputs/anomalies.csv",
    },
    {
        "step":    3,
        "script":  "allocate_water.py",
        "label":   "Allocation calculated",
        "desc":    "Calculating flow-based allocation → outputs/allocation_output.csv",
    },
    {
        "step":    4,
        "script":  "build_blockchain.py",
        "label":   "Blockchain built",
        "desc":    "SHA-256 chaining all blocks → outputs/blockchain_log.csv",
    },
    {
        "step":    5,
        "script":  "verify_blockchain.py",
        "label":   "Blockchain verified",
        "desc":    "Re-computing hashes — checking chain integrity",
    },
    {
        "step":    6,
        "script":  "generate_report.py",
        "label":   "Report ready",
        "desc":    "Assembling HTML report from all CSVs → outputs/water_report.html",
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────
WIDTH = 70

def banner(text, char="═"):
    return char * WIDTH + f"\n  {text}\n" + char * WIDTH

def step_box(step, total, desc):
    bar = "▓" * step + "░" * (total - step)
    return f"  [{bar}] {step}/{total}"

# ── Header ────────────────────────────────────────────────────────────────────
print()
print(banner("🚀  BLOCKCHAIN AI WATER MANAGEMENT — MASTER PIPELINE"))
print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  Scripts : {len(PIPELINE)} stages")
print()

start_total = time.time()
results     = []

# ── Execute each stage ────────────────────────────────────────────────────────
for stage in PIPELINE:
    step   = stage["step"]
    script = stage["script"]
    label  = stage["label"]
    desc   = stage["desc"]

    print("─" * WIDTH)
    print(f"  STEP {step}  │  {script}")
    print(f"  ↳ {desc}")
    print()

    t0 = time.time()
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            encoding="utf-8",     # decode subprocess output as UTF-8 on Windows
            check=True,
            cwd=SCRIPT_DIR,       # always run from WaterBlockchainProject/
            env=UTF8_ENV,         # tell Python subprocesses to use UTF-8 stdout
        )
        elapsed = time.time() - t0

        # Indent the script's own stdout neatly
        for line in result.stdout.strip().splitlines():
            print(f"    {line}")

        print()
        print(f"  ✅  Step {step} complete: {label}  ({elapsed:.2f}s)")
        print(step_box(step, len(PIPELINE), ""))
        results.append(("ok", step, label, elapsed))

    except subprocess.CalledProcessError as e:
        elapsed = time.time() - t0
        print()
        print(f"  ❌  STEP {step} FAILED — {script}")
        print(f"  Error after {elapsed:.2f}s:")
        print()
        for line in e.stderr.strip().splitlines():
            print(f"    {line}")
        print()
        print("─" * WIDTH)
        print(f"  Pipeline aborted at step {step}. Fix the error above and re-run.")
        print("─" * WIDTH)
        sys.exit(1)

    print()

# ── Summary table ─────────────────────────────────────────────────────────────
total_time = time.time() - start_total

print("═" * WIDTH)
print("  PIPELINE SUMMARY")
print("═" * WIDTH)
print(f"  {'Step':<6} {'Script':<25} {'Status':<10} {'Time':>7}")
print("  " + "─" * 54)
for status, step, label, elapsed in results:
    icon = "✅" if status == "ok" else "❌"
    print(f"  {step:<6} {PIPELINE[step-1]['script']:<25} {icon} OK     {elapsed:>5.2f}s")
print("  " + "─" * 54)
print(f"  {'Total':>32}  {total_time:>6.2f}s")
print()
print("═" * WIDTH)
print()
print("  🎉  PIPELINE COMPLETE — Open outputs/water_report.html to view results")
print()
print(f"  Output files (outputs/):")
outputs = [
    ("water_data.csv",        "50 sensor readings"),
    ("anomalies.csv",         "WHO standard violations"),
    ("allocation_output.csv", "Flow-based water allocation"),
    ("blockchain_log.csv",    "SHA-256 tamper-proof ledger"),
    ("water_report.html",     "Full HTML dashboard report"),
]
for fname, desc in outputs:
    print(f"    📄 {fname:<26} — {desc}")
print()
print("═" * WIDTH)
