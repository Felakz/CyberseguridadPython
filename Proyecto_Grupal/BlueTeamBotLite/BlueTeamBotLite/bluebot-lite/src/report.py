from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Sin GUI
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from datetime import datetime, timedelta
from .utils import REPORTS_DIR
from .db import get_severity_trends, get_host_trends
import io

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

    # Gráfico de tendencias (últimos 30 días)
    try:
        trend_img = _generate_trend_chart()
        if trend_img:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, y, "Tendencia de Severidades (30 días)")
            y -= 0.5*cm
            c.drawImage(ImageReader(trend_img), 2*cm, y-6*cm, width=16*cm, height=6*cm)
            y -= 6.5*cm
    except Exception as e:
        print(f"[WARN] No se pudo generar gráfico de tendencias: {e}")

    # Gráfico de distribución por severidad
    if sev_counts['HIGH'] + sev_counts['MEDIUM'] + sev_counts['LOW'] > 0:
        try:
            pie_img = _generate_severity_pie(sev_counts)
            if pie_img:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(2*cm, y, "Distribución de Severidades")
                y -= 0.5*cm
                c.drawImage(ImageReader(pie_img), 2*cm, y-6*cm, width=8*cm, height=6*cm)
                y -= 7*cm
        except Exception as e:
            print(f"[WARN] No se pudo generar gráfico de pastel: {e}")

    # Top hallazgos (nueva página si es necesario)
    if y < 8*cm:
        c.showPage()
        y = height - 2*cm
    
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


def _generate_trend_chart():
    """Genera gráfico de líneas con tendencias de severidad"""
    try:
        trends = get_severity_trends(days=30)
        if not trends['dates']:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(trends['dates'], trends['HIGH'], 'r-', label='HIGH', linewidth=2, marker='o')
        ax.plot(trends['dates'], trends['MEDIUM'], 'orange', label='MEDIUM', linewidth=2, marker='s')
        ax.plot(trends['dates'], trends['LOW'], 'y-', label='LOW', linewidth=2, marker='^')
        
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de Hallazgos')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        return buf
    except Exception as e:
        print(f"[WARN] Error generando trend chart: {e}")
        return None


def _generate_severity_pie(sev_counts):
    """Genera gráfico de pastel con distribución de severidades"""
    try:
        labels = []
        sizes = []
        colors = []
        
        if sev_counts['HIGH'] > 0:
            labels.append(f"HIGH ({sev_counts['HIGH']})")
            sizes.append(sev_counts['HIGH'])
            colors.append('#ff4444')
        if sev_counts['MEDIUM'] > 0:
            labels.append(f"MEDIUM ({sev_counts['MEDIUM']})")
            sizes.append(sev_counts['MEDIUM'])
            colors.append('#ffaa00')
        if sev_counts['LOW'] > 0:
            labels.append(f"LOW ({sev_counts['LOW']})")
            sizes.append(sev_counts['LOW'])
            colors.append('#ffff00')
        
        if not sizes:
            return None
        
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        return buf
    except Exception as e:
        print(f"[WARN] Error generando pie chart: {e}")
        return None


def generate_comparison_report(range1_start, range1_end, range2_start, range2_end):
    """
    Genera un reporte PDF comparando dos rangos de fechas
    
    Args:
        range1_start, range1_end: datetime para primer rango
        range2_start, range2_end: datetime para segundo rango
    
    Returns:
        Path del PDF generado
    """
    from .db import compare_date_ranges
    
    comparison = compare_date_ranges(range1_start, range1_end, range2_start, range2_end)
    ts = int(datetime.now().timestamp())
    out = REPORTS_DIR / f"comparison_{ts}.pdf"
    
    c = canvas.Canvas(str(out), pagesize=A4)
    width, height = A4
    c.setTitle("BlueBot Comparison Report")
    
    y = height - 2*cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, y, "Reporte Comparativo")
    y -= 1.5*cm
    
    # Rango 1
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, f"Período 1: {range1_start.strftime('%Y-%m-%d')} a {range1_end.strftime('%Y-%m-%d')}")
    y -= 0.7*cm
    c.setFont("Helvetica", 11)
    r1 = comparison['range1']['analysis']
    c.drawString(2.5*cm, y, f"Total hallazgos: {r1['total']}")
    y -= 0.5*cm
    c.drawString(2.5*cm, y, f"HIGH: {r1['severity']['HIGH']}  MEDIUM: {r1['severity']['MEDIUM']}  LOW: {r1['severity']['LOW']}")
    y -= 1.2*cm
    
    # Rango 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, f"Período 2: {range2_start.strftime('%Y-%m-%d')} a {range2_end.strftime('%Y-%m-%d')}")
    y -= 0.7*cm
    c.setFont("Helvetica", 11)
    r2 = comparison['range2']['analysis']
    c.drawString(2.5*cm, y, f"Total hallazgos: {r2['total']}")
    y -= 0.5*cm
    c.drawString(2.5*cm, y, f"HIGH: {r2['severity']['HIGH']}  MEDIUM: {r2['severity']['MEDIUM']}  LOW: {r2['severity']['LOW']}")
    y -= 1.2*cm
    
    # Delta
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Cambios (Período 2 vs Período 1)")
    y -= 0.7*cm
    c.setFont("Helvetica", 11)
    delta = comparison['delta']
    delta_sign = lambda x: f"+{x}" if x > 0 else str(x)
    c.drawString(2.5*cm, y, f"Total: {delta_sign(delta['total'])}")
    y -= 0.5*cm
    c.drawString(2.5*cm, y, f"HIGH: {delta_sign(delta['severity']['HIGH'])}  MEDIUM: {delta_sign(delta['severity']['MEDIUM'])}  LOW: {delta_sign(delta['severity']['LOW'])}")
    y -= 1.2*cm
    
    # Top hosts afectados
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Top 5 Hosts (Período 2)")
    y -= 0.7*cm
    c.setFont("Helvetica", 10)
    for host, count in r2['top_hosts']:
        c.drawString(2.5*cm, y, f"{host}: {count} hallazgos")
        y -= 0.5*cm
    
    c.showPage()
    c.save()
    print(f"[OK] Reporte comparativo generado: {out}")
    return out
