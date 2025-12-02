from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Agregar src al path para importar módulos
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from src.db import (
    init_db, 
    get_statistics, 
    get_severity_trends, 
    get_host_trends,
    get_scans_by_date_range,
    compare_date_ranges
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blueteambot-secret-key-change-in-production'

# Inicializar BD al arranque
init_db()


@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')


@app.route('/estadisticas')
def estadisticas():
    """Página de estadísticas generales"""
    return render_template('stats.html')


@app.route('/comparar')
def comparar():
    """Página de comparativas por fechas"""
    return render_template('comparar.html')


@app.route('/tendencias')
def tendencias():
    """Página de tendencias temporales"""
    return render_template('tendencias.html')


@app.route('/scans')
def scans():
    """Página de historial de escaneos"""
    return render_template('scans.html')


# ============================================================================
# API ENDPOINTS (JSON)
# ============================================================================

@app.route('/api/stats')
def api_stats():
    """Devuelve estadísticas generales en JSON"""
    try:
        stats = get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/severity-trends')
def api_severity_trends():
    """Devuelve tendencias de severidad en JSON"""
    try:
        days = request.args.get('days', 30, type=int)
        trends = get_severity_trends(days=days)
        
        # Convertir datetime a strings para JSON
        data = {
            'dates': [d.strftime('%Y-%m-%d %H:%M') for d in trends['dates']],
            'HIGH': trends['HIGH'],
            'MEDIUM': trends['MEDIUM'],
            'LOW': trends['LOW']
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/host-trends')
def api_host_trends():
    """Devuelve tendencias por host en JSON"""
    try:
        days = request.args.get('days', 30, type=int)
        trends = get_host_trends(days=days)
        
        # Convertir datetime a strings
        data = {}
        for host, values in trends.items():
            data[host] = {
                'dates': [d.strftime('%Y-%m-%d %H:%M') for d in values['dates']],
                'HIGH': values['HIGH'],
                'MEDIUM': values['MEDIUM'],
                'LOW': values['LOW']
            }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scans')
def api_scans():
    """Devuelve lista de escaneos en un rango de fechas"""
    try:
        # Parámetros opcionales
        days = request.args.get('days', 30, type=int)
        date_from = datetime.utcnow() - timedelta(days=days)
        date_to = datetime.utcnow()
        
        scans = get_scans_by_date_range(date_from, date_to)
        
        data = []
        for scan in scans:
            data.append({
                'id': scan.id,
                'timestamp': scan.timestamp,
                'created_at': scan.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'total_findings': scan.total_findings
            })
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """Compara dos rangos de fechas"""
    try:
        data = request.get_json()
        
        # Parsear fechas
        r1_start = datetime.fromisoformat(data['range1_start'])
        r1_end = datetime.fromisoformat(data['range1_end'])
        r2_start = datetime.fromisoformat(data['range2_start'])
        r2_end = datetime.fromisoformat(data['range2_end'])
        
        comparison = compare_date_ranges(r1_start, r1_end, r2_start, r2_end)
        
        # Serializar fechas
        result = {
            'range1': {
                'start': r1_start.strftime('%Y-%m-%d'),
                'end': r1_end.strftime('%Y-%m-%d'),
                'analysis': comparison['range1']['analysis']
            },
            'range2': {
                'start': r2_start.strftime('%Y-%m-%d'),
                'end': r2_end.strftime('%Y-%m-%d'),
                'analysis': comparison['range2']['analysis']
            },
            'delta': comparison['delta']
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan/<int:scan_id>/findings')
def api_scan_findings(scan_id):
    """Devuelve los findings de un escaneo específico"""
    try:
        from src.db.models import get_session, Scan
        import json
        
        session = get_session()
        scan = session.query(Scan).filter_by(id=scan_id).first()
        
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        findings = []
        for f in scan.findings:
            findings.append({
                'host': f.host,
                'port': f.port,
                'service': f.service,
                'product': f.product,
                'version': f.version,
                'severity': f.severity,
                'reasons': json.loads(f.reasons) if f.reasons else [],
                'status': f.status
            })
        
        session.close()
        return jsonify(findings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("  BlueTeamBot Dashboard Web - Iniciando...")
    print("=" * 70)
    print("  Accede desde: http://localhost:5000")
    print("  Presiona Ctrl+C para detener")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
