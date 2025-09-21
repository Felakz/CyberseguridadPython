import argparse
import time
from datetime import datetime
from . import scan, rules, diff, report
from .utils import load_json, save_json, BASELINE_FILE, RUNS_DIR

def run_once():
    # 1) Escaneo
    data = scan.run_scan()
    ts = data["ts"]
    raw_file = RUNS_DIR / f"raw_{ts}.json"
    save_json(raw_file, data)

    # 2) Evaluar contra reglas
    evals = rules.evaluate(data["findings"])

    # 3) Diff vs baseline
    baseline = load_json(BASELINE_FILE, default={"findings":[]}).get("findings", [])
    changes = diff.diff_vs_baseline(evals, baseline)

    # 4) Guardar baseline nuevo
    save_json(BASELINE_FILE, {"ts": ts, "findings": evals})

    # 5) Reportes
    csv_path = report.save_csv(ts, changes or evals)
    pdf_path = report.save_pdf(ts, changes or evals)

    print(f"[OK] Escaneo {ts}")
    print(f" - CSV: {csv_path}")
    print(f" - PDF: {pdf_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="Ejecuta solo una vez y sale")
    ap.add_argument("--schedule", action="store_true", help="Ejecuta cada día a las 20:00 (simple)")
    args = ap.parse_args()

    if args.once or not args.schedule:
        run_once()
        return

    print("[SCHEDULE] corriendo cada día a las 20:00...")
    while True:
        now = datetime.now()
        if now.hour == 20 and now.minute == 0:
            run_once()
            time.sleep(60)
        time.sleep(1)

if __name__ == "__main__":
    main()
