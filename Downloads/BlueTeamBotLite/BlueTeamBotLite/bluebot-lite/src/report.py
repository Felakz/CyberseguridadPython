from pathlib import Path
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from .utils import REPORTS_DIR

def save_csv(ts, rows):
    df = pd.DataFrame(rows)
    out = REPORTS_DIR / f"findings_{ts}.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    return out

def save_pdf(ts, rows):
    out = REPORTS_DIR / f"report_{ts}.pdf"
    c = canvas.Canvas(str(out), pagesize=A4)
    width, height = A4
    c.setTitle(f"BlueBot Report {ts}")

    # Título
    y = height - 2*cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, f"Blue Team Bot – Resumen {ts}")
    y -= 1.2*cm

    # Resumen ejecutivo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Resumen Ejecutivo")
    y -= 0.7*cm
    sev_counts = {"HIGH":0, "MEDIUM":0, "LOW":0}
    for r in rows:
        sev = r.get("severity")
        if sev in sev_counts:
            sev_counts[sev] += 1
    c.setFont("Helvetica", 11)
    c.drawString(2*cm, y, f"Altos: {sev_counts['HIGH']}  Medios: {sev_counts['MEDIUM']}  Bajos: {sev_counts['LOW']}")
    y -= 1.0*cm

    # Top hallazgos (primeros 10)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Top Hallazgos")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    for r in rows[:10]:
        line = f"{r['host']}:{r['port']} [{r.get('severity','?')}] - {', '.join(r.get('reasons', []))}"
        c.drawString(2*cm, y, line[:100])
        y -= 0.55*cm
        if y < 2*cm:
            c.showPage()
            y = height - 2*cm
            c.setFont("Helvetica", 10)

    c.showPage()
    c.save()
    return out
