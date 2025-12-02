#!/usr/bin/env python3
"""
BlueTeamBot Lite - Aplicación Unificada
========================================
Combina el escáner de red con el dashboard web en un solo archivo ejecutable.

Uso:
    python bluebot_unified.py                    # Menú interactivo
    python bluebot_unified.py --scan             # Ejecutar solo escaneo
    python bluebot_unified.py --dashboard        # Iniciar solo dashboard
    python bluebot_unified.py --scan-and-serve   # Escanear y luego servir dashboard
"""

import sys
import argparse
from pathlib import Path

# Flask y dependencias web
try:
    from flask import Flask, render_template, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[WARN] Flask no instalado. Instala con: pip install flask")

from datetime import datetime, timedelta

# Importar módulos del proyecto
try:
    from src import scan, rules, diff, report
    from src.utils import load_json, save_json, BASELINE_FILE, RUNS_DIR, REPORTS_DIR
    from src.db import (
        init_db, get_session,
        save_scan_to_db, get_scans_by_date_range, compare_date_ranges,
        get_host_trends, get_severity_trends, get_statistics
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"[ERROR] No se pudieron importar módulos del proyecto: {e}")
    print("[INFO] Asegúrate de ejecutar desde el directorio del proyecto")
    print("[INFO] Y que todas las dependencias estén instaladas: pip install -r requirements.txt")

# ============================================================================
# SECCIÓN 1: FUNCIONES DE ESCANEO
# ============================================================================

def ejecutar_escaneo_completo(mostrar_progreso=True):
    """
    Ejecuta un ciclo completo de escaneo: scan → rules → diff → report → DB
    
    Returns:
        dict: Resultados del escaneo con estadísticas
    """
    if not MODULES_AVAILABLE:
        print("\n[ERROR] No se pueden ejecutar escaneos. Módulos no disponibles.")
        return None
    
    if mostrar_progreso:
        print("\n" + "="*70)
        print("  🔍 BlueTeamBot Lite - Iniciando Escaneo")
        print("="*70)
    
    # 1. Ejecutar escaneo con nmap
    if mostrar_progreso:
        print(f"\n[1/4] 🌐 Escaneando red con nmap...")
    
    data = scan.run_scan()
    ts = data["ts"]
    findings = data["findings"]
    
    if mostrar_progreso:
        print(f"      ✓ Escaneo completado (timestamp: {ts})")
    
    # 2. Evaluar contra reglas
    if mostrar_progreso:
        print(f"\n[2/4] ⚖️  Evaluando reglas de seguridad...")
    
    evals = rules.evaluate(findings)
    
    # Calcular severidades
    findings_count = len(evals)
    high = sum(1 for f in evals if f.get('severity') == 'HIGH')
    medium = sum(1 for f in evals if f.get('severity') == 'MEDIUM')
    low = sum(1 for f in evals if f.get('severity') == 'LOW')
    
    if mostrar_progreso:
        print(f"      ✓ {findings_count} hallazgos encontrados")
        print(f"        └─ HIGH: {high} | MEDIUM: {medium} | LOW: {low}")
    
    # 3. Comparar con baseline
    if mostrar_progreso:
        print(f"\n[3/4] 📊 Comparando con baseline...")
    
    baseline = load_json(BASELINE_FILE, default={"findings":[]}).get("findings", [])
    changes = diff.diff_vs_baseline(evals, baseline)
    
    if mostrar_progreso:
        if changes:
            print(f"      ✓ {len(changes)} cambios detectados")
        else:
            print(f"      ✓ Sin cambios respecto al baseline")
    
    # Actualizar baseline
    save_json(BASELINE_FILE, {"ts": ts, "findings": evals})
    
    # 4. Generar reportes
    if mostrar_progreso:
        print(f"\n[4/4] 📄 Generando reportes...")
    
    csv_file = REPORTS_DIR / f'findings_{ts}.csv'
    pdf_file = REPORTS_DIR / f'findings_{ts}.pdf'
    raw_file = RUNS_DIR / f'raw_{ts}.json'
    
    report.save_csv(changes or evals, csv_file)
    report.save_pdf(changes or evals, pdf_file)
    save_json(raw_file, data)
    
    if mostrar_progreso:
        print(f"      ✓ CSV: {csv_file.name}")
        print(f"      ✓ PDF: {pdf_file.name}")
        print(f"      ✓ JSON: {raw_file.name}")
    
    # 5. Guardar en base de datos
    if mostrar_progreso:
        print(f"\n[5/5] 💾 Guardando en base de datos...")
    
    try:
        save_scan_to_db(data, changes or evals)
        if mostrar_progreso:
            print(f"      ✓ Datos persistidos en SQLite")
    except Exception as e:
        if mostrar_progreso:
            print(f"      ✗ Error guardando en BD: {e}")
    
    if mostrar_progreso:
        print("\n" + "="*70)
        print("  ✅ Escaneo completado exitosamente")
        print("="*70 + "\n")
    
    return {
        'timestamp': ts,
        'findings': len(evals),
        'severity': {'HIGH': high, 'MEDIUM': medium, 'LOW': low},
        'files': {
            'csv': str(csv_file),
            'pdf': str(pdf_file),
            'json': str(raw_file)
        }
    }


# ============================================================================
# SECCIÓN 2: DASHBOARD WEB (FLASK)
# ============================================================================

# Crear app Flask y rutas solo si las dependencias están disponibles
if FLASK_AVAILABLE and MODULES_AVAILABLE:
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False  # Soporte UTF-8 en JSON

    # Inicializar BD al arrancar
    init_db()

    @app.route('/')
    def index():
        """Página principal del dashboard"""
        return render_template('index.html')

    @app.route('/stats')
    def stats_page():
        """Página de estadísticas detalladas"""
        return render_template('stats.html')

    @app.route('/tendencias')
    def tendencias_page():
        """Página de análisis temporal"""
        return render_template('tendencias.html')

    @app.route('/comparar')
    def comparar_page():
        """Página de comparación de fechas"""
        return render_template('comparar.html')

    @app.route('/scans')
    def scans_page():
        """Página de historial de escaneos"""
        return render_template('scans.html')

    # API Endpoints
    @app.route('/api/stats')
    def api_stats():
        """Obtiene estadísticas generales"""
        try:
            stats = get_statistics()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/severity-trends')
    def api_severity_trends():
        """Obtiene tendencias de severidad"""
        try:
            days = request.args.get('days', 30, type=int)
            
            trends = get_severity_trends(days)
            
            # Convertir datetime a string para JSON
            trends['dates'] = [d.isoformat() if isinstance(d, datetime) else d for d in trends['dates']]
            
            return jsonify(trends)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/host-trends')
    def api_host_trends():
        """Obtiene tendencias por host"""
        try:
            days = request.args.get('days', 30, type=int)
            
            trends = get_host_trends(days)
            
            # Convertir datetime a string
            for host_data in trends:
                host_data['dates'] = [d.isoformat() if isinstance(d, datetime) else d for d in host_data['dates']]
            
            return jsonify(trends)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/scans')
    def api_scans():
        """Obtiene lista de todos los escaneos"""
        try:
            days = request.args.get('days', 90, type=int)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            scans = get_scans_by_date_range(start_date, end_date)
            
            # Formatear para JSON
            result = []
            for scan in scans:
                result.append({
                    'id': scan['id'],
                    'created_at': scan['created_at'].isoformat() if isinstance(scan['created_at'], datetime) else scan['created_at'],
                    'hosts_count': scan['hosts_count'],
                    'findings_count': scan['findings_count']
                })
            
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/compare', methods=['POST'])
    def api_compare():
        """Compara dos rangos de fechas"""
        try:
            data = request.json
            
            period1_start = datetime.fromisoformat(data['period1_start'])
            period1_end = datetime.fromisoformat(data['period1_end'])
            period2_start = datetime.fromisoformat(data['period2_start'])
            period2_end = datetime.fromisoformat(data['period2_end'])
            
            comparison = compare_date_ranges(
                period1_start, period1_end,
                period2_start, period2_end
            )
            
            return jsonify(comparison)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/scan/run', methods=['POST'])
    def api_run_scan():
        """
        Endpoint para ejecutar un escaneo desde el dashboard
        """
        try:
            resultado = ejecutar_escaneo_completo(mostrar_progreso=False)
            return jsonify({
                'success': True,
                'message': 'Escaneo completado exitosamente',
                'data': resultado
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


def iniciar_dashboard(host='0.0.0.0', port=5000, debug=True):
    """
    Inicia el servidor web Flask
    
    Args:
        host: IP donde escuchar (0.0.0.0 = todas las interfaces)
        port: Puerto del servidor
        debug: Modo debug de Flask
    """
    if not FLASK_AVAILABLE or not MODULES_AVAILABLE:
        print("\n[ERROR] No se puede iniciar el dashboard.")
        print("[INFO] Asegúrate de que Flask y todos los módulos estén instalados.")
        return
    
    print("\n" + "="*70)
    print("  🌐 BlueTeamBot Dashboard Web - Iniciando...")
    print("="*70)
    print(f"  Accede desde: http://localhost:{port}")
    print(f"  Presiona Ctrl+C para detener")
    print("="*70 + "\n")
    
    app.run(host=host, port=port, debug=debug)


# ============================================================================
# SECCIÓN 3: MENÚ INTERACTIVO
# ============================================================================

def mostrar_menu():
    """Muestra el menú principal de la aplicación"""
    if not MODULES_AVAILABLE:
        print("\n[ERROR] Módulos del proyecto no disponibles.")
        print("[INFO] Instala las dependencias: pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("  🛡️  BlueTeamBot Lite - Aplicación Unificada")
    print("="*70)
    print("\n  Selecciona una opción:\n")
    print("  [1] 🔍 Ejecutar Escaneo de Red")
    print("  [2] 🌐 Iniciar Dashboard Web")
    print("  [3] 🚀 Escanear y luego Iniciar Dashboard")
    print("  [4] ❌ Salir")
    print("\n" + "="*70)
    
    while True:
        try:
            opcion = input("\n  Opción: ").strip()
            
            if opcion == '1':
                ejecutar_escaneo_completo(mostrar_progreso=True)
                input("\n  Presiona ENTER para volver al menú...")
                mostrar_menu()
                break
            
            elif opcion == '2':
                iniciar_dashboard()
                break
            
            elif opcion == '3':
                print("\n  ⚡ Modo combinado: Escaneo + Dashboard")
                ejecutar_escaneo_completo(mostrar_progreso=True)
                print("\n  📊 Datos actualizados, iniciando dashboard...\n")
                iniciar_dashboard()
                break
            
            elif opcion == '4':
                print("\n  👋 ¡Hasta pronto!\n")
                sys.exit(0)
            
            else:
                print("  ⚠️  Opción inválida, intenta de nuevo")
        
        except KeyboardInterrupt:
            print("\n\n  👋 Operación cancelada. ¡Hasta pronto!\n")
            sys.exit(0)


# ============================================================================
# SECCIÓN 4: PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='BlueTeamBot Lite - Escáner de Red y Dashboard Unificado',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python bluebot_unified.py                    # Menú interactivo
  python bluebot_unified.py --scan             # Solo escaneo
  python bluebot_unified.py --dashboard        # Solo dashboard
  python bluebot_unified.py --scan-and-serve   # Escaneo + Dashboard
  python bluebot_unified.py -d --port 8080     # Dashboard en puerto 8080
        """
    )
    
    parser.add_argument(
        '--scan', '-s',
        action='store_true',
        help='Ejecutar solo el escaneo de red'
    )
    
    parser.add_argument(
        '--dashboard', '-d',
        action='store_true',
        help='Iniciar solo el dashboard web'
    )
    
    parser.add_argument(
        '--scan-and-serve', '-ss',
        action='store_true',
        help='Escanear primero y luego iniciar dashboard'
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5000,
        help='Puerto para el dashboard web (default: 5000)'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='IP donde escuchar (default: 0.0.0.0 = todas las interfaces)'
    )
    
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Desactivar modo debug de Flask'
    )
    
    args = parser.parse_args()
    
    # Inicializar base de datos solo si los módulos están disponibles
    if MODULES_AVAILABLE:
        init_db()
    
    # Procesar argumentos
    if args.scan:
        ejecutar_escaneo_completo(mostrar_progreso=True)
    
    elif args.dashboard:
        iniciar_dashboard(
            host=args.host,
            port=args.port,
            debug=not args.no_debug
        )
    
    elif args.scan_and_serve:
        print("\n  ⚡ Modo combinado: Escaneo + Dashboard\n")
        ejecutar_escaneo_completo(mostrar_progreso=True)
        print("\n  📊 Datos actualizados, iniciando dashboard...\n")
        iniciar_dashboard(
            host=args.host,
            port=args.port,
            debug=not args.no_debug
        )
    
    else:
        # Sin argumentos = mostrar menú interactivo
        mostrar_menu()


if __name__ == '__main__':
    main()
