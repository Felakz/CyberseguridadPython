import json
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import func
from .models import Scan, Finding, get_session


def save_scan_to_db(scan_data, evaluated_findings):
    """
    Guarda un escaneo y sus hallazgos en la base de datos
    
    Args:
        scan_data: dict con 'ts' y 'findings' del escaneo
        evaluated_findings: lista de findings evaluados con severidad
    """
    session = get_session()
    try:
        # Crear registro de escaneo
        scan = Scan(
            timestamp=scan_data['ts'],
            total_findings=len(evaluated_findings)
        )
        session.add(scan)
        session.flush()  # Para obtener el scan.id
        
        # Crear hallazgos
        for f in evaluated_findings:
            finding = Finding(
                scan_id=scan.id,
                host=f.get('host', ''),
                port=f.get('port', 0),
                service=f.get('service', ''),
                product=f.get('product', ''),
                version=f.get('version', ''),
                env=f.get('env', ''),
                severity=f.get('severity', ''),
                reasons=json.dumps(f.get('reasons', [])),
                status=f.get('status', 'NEW')
            )
            session.add(finding)
        
        session.commit()
        print(f"[DB] Guardado scan {scan_data['ts']} con {len(evaluated_findings)} hallazgos")
        return scan.id
        
    except Exception as e:
        session.rollback()
        print(f"[DB ERROR] {e}")
        raise
    finally:
        session.close()


def get_scans_by_date_range(date_from=None, date_to=None):
    """
    Obtiene todos los escaneos en un rango de fechas
    
    Args:
        date_from: datetime o None (últimos 30 días)
        date_to: datetime o None (ahora)
    
    Returns:
        Lista de objetos Scan con sus findings
    """
    session = get_session()
    try:
        query = session.query(Scan)
        
        if date_from is None:
            date_from = datetime.utcnow() - timedelta(days=30)
        if date_to is None:
            date_to = datetime.utcnow()
        
        scans = query.filter(
            Scan.created_at.between(date_from, date_to)
        ).order_by(Scan.created_at).all()
        
        return scans
    finally:
        session.close()


def compare_date_ranges(range1_start, range1_end, range2_start, range2_end):
    """
    Compara dos rangos de fechas y devuelve análisis comparativo
    
    Returns:
        dict con comparativa de severidades, hosts, cambios
    """
    session = get_session()
    try:
        # Obtener findings del rango 1
        findings1 = session.query(Finding).join(Scan).filter(
            Scan.created_at.between(range1_start, range1_end)
        ).all()
        
        # Obtener findings del rango 2
        findings2 = session.query(Finding).join(Scan).filter(
            Scan.created_at.between(range2_start, range2_end)
        ).all()
        
        def analyze_findings(findings):
            severity_count = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            host_issues = defaultdict(int)
            port_issues = defaultdict(int)
            
            for f in findings:
                if f.severity:
                    severity_count[f.severity] = severity_count.get(f.severity, 0) + 1
                host_issues[f.host] += 1
                port_issues[f.port] += 1
            
            return {
                'total': len(findings),
                'severity': severity_count,
                'top_hosts': sorted(host_issues.items(), key=lambda x: x[1], reverse=True)[:5],
                'top_ports': sorted(port_issues.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        
        analysis1 = analyze_findings(findings1)
        analysis2 = analyze_findings(findings2)
        
        # Calcular cambios
        delta = {
            'total': analysis2['total'] - analysis1['total'],
            'severity': {
                'HIGH': analysis2['severity']['HIGH'] - analysis1['severity']['HIGH'],
                'MEDIUM': analysis2['severity']['MEDIUM'] - analysis1['severity']['MEDIUM'],
                'LOW': analysis2['severity']['LOW'] - analysis1['severity']['LOW']
            }
        }
        
        return {
            'range1': {
                'start': range1_start,
                'end': range1_end,
                'analysis': analysis1
            },
            'range2': {
                'start': range2_start,
                'end': range2_end,
                'analysis': analysis2
            },
            'delta': delta
        }
        
    finally:
        session.close()


def get_host_trends(days=30):
    """
    Obtiene tendencias por host en los últimos N días
    
    Returns:
        dict: {host: {scan_dates: [...], high_counts: [...], medium_counts: [...], low_counts: [...]}}
    """
    session = get_session()
    try:
        date_from = datetime.utcnow() - timedelta(days=days)
        
        scans = session.query(Scan).filter(
            Scan.created_at >= date_from
        ).order_by(Scan.created_at).all()
        
        trends = defaultdict(lambda: {
            'dates': [],
            'HIGH': [],
            'MEDIUM': [],
            'LOW': []
        })
        
        for scan in scans:
            host_sev = defaultdict(lambda: {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0})
            
            for finding in scan.findings:
                if finding.severity:
                    host_sev[finding.host][finding.severity] += 1
            
            # Agregar puntos de datos para cada host
            for host, counts in host_sev.items():
                trends[host]['dates'].append(scan.created_at)
                trends[host]['HIGH'].append(counts['HIGH'])
                trends[host]['MEDIUM'].append(counts['MEDIUM'])
                trends[host]['LOW'].append(counts['LOW'])
        
        return dict(trends)
        
    finally:
        session.close()


def get_severity_trends(days=30):
    """
    Obtiene tendencia global de severidades en los últimos N días
    
    Returns:
        dict: {dates: [...], high: [...], medium: [...], low: [...]}
    """
    session = get_session()
    try:
        date_from = datetime.utcnow() - timedelta(days=days)
        
        scans = session.query(Scan).filter(
            Scan.created_at >= date_from
        ).order_by(Scan.created_at).all()
        
        dates = []
        high_counts = []
        medium_counts = []
        low_counts = []
        
        for scan in scans:
            severity_count = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            
            for finding in scan.findings:
                if finding.severity:
                    severity_count[finding.severity] += 1
            
            dates.append(scan.created_at)
            high_counts.append(severity_count['HIGH'])
            medium_counts.append(severity_count['MEDIUM'])
            low_counts.append(severity_count['LOW'])
        
        return {
            'dates': dates,
            'HIGH': high_counts,
            'MEDIUM': medium_counts,
            'LOW': low_counts
        }
        
    finally:
        session.close()


def get_statistics():
    """Devuelve estadísticas generales de la base de datos"""
    session = get_session()
    try:
        total_scans = session.query(func.count(Scan.id)).scalar()
        total_findings = session.query(func.count(Finding.id)).scalar()
        
        # Últimos 7 días
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_scans = session.query(func.count(Scan.id)).filter(
            Scan.created_at >= week_ago
        ).scalar()
        
        # Severidades totales
        high = session.query(func.count(Finding.id)).filter(Finding.severity == 'HIGH').scalar()
        medium = session.query(func.count(Finding.id)).filter(Finding.severity == 'MEDIUM').scalar()
        low = session.query(func.count(Finding.id)).filter(Finding.severity == 'LOW').scalar()
        
        return {
            'total_scans': total_scans,
            'total_findings': total_findings,
            'recent_scans': recent_scans,
            'severity_totals': {
                'HIGH': high,
                'MEDIUM': medium,
                'LOW': low
            }
        }
    finally:
        session.close()
