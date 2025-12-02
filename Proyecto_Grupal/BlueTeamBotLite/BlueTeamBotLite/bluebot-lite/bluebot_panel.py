#!/usr/bin/env python3
"""
BlueTeamBot Lite - Panel Dashboard
===================================
Interfaz web interactiva usando Panel (HoloViz)

Uso:
    python bluebot_panel.py
"""

import panel as pn
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# Importar módulos del proyecto
try:
    from src import scan, rules, diff, report
    from src.utils import load_json, save_json, BASELINE_FILE, RUNS_DIR, REPORTS_DIR
    from src.db import (
        init_db, get_session,
        save_scan_to_db, get_scans_by_date_range,
        get_host_trends, get_severity_trends, get_statistics
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"[ERROR] Módulos no disponibles: {e}")

# Inicializar Panel
pn.extension('plotly', 'tabulator', notifications=True)

# ============================================================================
# FUNCIONES DE ESCANEO
# ============================================================================

def ejecutar_escaneo():
    """Ejecuta un escaneo completo y retorna los resultados"""
    if not MODULES_AVAILABLE:
        return None
    
    try:
        # 1. Escaneo
        data = scan.run_scan()
        ts = data["ts"]
        findings = data["findings"]
        
        # 2. Evaluar reglas
        evals = rules.evaluate(findings)
        
        # 3. Comparar con baseline
        baseline = load_json(BASELINE_FILE, default={"findings":[]}).get("findings", [])
        changes = diff.diff_vs_baseline(evals, baseline)
        save_json(BASELINE_FILE, {"ts": ts, "findings": evals})
        
        # 4. Generar reportes
        csv_file = REPORTS_DIR / f'findings_{ts}.csv'
        pdf_file = REPORTS_DIR / f'findings_{ts}.pdf'
        raw_file = RUNS_DIR / f'raw_{ts}.json'
        
        report.save_csv(changes or evals, csv_file)
        report.save_pdf(changes or evals, pdf_file)
        save_json(raw_file, data)
        
        # 5. Guardar en BD
        save_scan_to_db(data, changes or evals)
        
        return {
            'timestamp': ts,
            'findings': len(evals),
            'csv': str(csv_file),
            'pdf': str(pdf_file)
        }
    except Exception as e:
        return {'error': str(e)}

# ============================================================================
# COMPONENTES DE INTERFAZ
# ============================================================================

class BlueTeamDashboard:
    def __init__(self):
        # Inicializar BD
        if MODULES_AVAILABLE:
            init_db()
        
        # Variables de estado
        self.stats = {}
        self.scanning = False
        
        # Crear widgets
        self.create_widgets()
        self.create_layout()
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Título
        self.title = pn.pane.Markdown(
            "# 🛡️ BlueTeamBot Lite - Dashboard",
            styles={'background': '#1f77b4', 'color': 'white', 'padding': '20px'}
        )
        
        # Botones de acción
        self.btn_scan = pn.widgets.Button(
            name='▶️ Ejecutar Escaneo', 
            button_type='primary',
            width=200
        )
        self.btn_scan.on_click(self.on_scan_click)
        
        self.btn_refresh = pn.widgets.Button(
            name='🔄 Actualizar Datos',
            button_type='success',
            width=200
        )
        self.btn_refresh.on_click(self.on_refresh_click)
        
        # Indicadores de estadísticas
        self.card_total_scans = pn.indicators.Number(
            name='Total Escaneos',
            value=0,
            format='{value:,}',
            colors=[(0.8, 'green'), (1, 'gold')],
            default_color='blue',
            font_size='36pt'
        )
        
        self.card_total_findings = pn.indicators.Number(
            name='Total Hallazgos',
            value=0,
            format='{value:,}',
            colors=[(0.8, 'orange'), (1, 'red')],
            default_color='orange',
            font_size='36pt'
        )
        
        self.card_high_severity = pn.indicators.Number(
            name='Severidad ALTA',
            value=0,
            format='{value:,}',
            default_color='red',
            font_size='36pt'
        )
        
        self.card_recent_scans = pn.indicators.Number(
            name='Últimos 7 días',
            value=0,
            format='{value:,}',
            default_color='green',
            font_size='36pt'
        )
        
        # Selector de días para gráficos
        self.days_selector = pn.widgets.IntSlider(
            name='Días de Tendencia',
            start=7,
            end=90,
            step=7,
            value=30,
            width=400
        )
        self.days_selector.param.watch(self.on_days_change, 'value')
        
        # Gráficos (vacíos inicialmente)
        self.severity_chart = pn.pane.Plotly(self.create_empty_chart())
        self.trend_chart = pn.pane.Plotly(self.create_empty_chart())
        
        # Tabla de escaneos recientes
        self.scans_table = pn.widgets.Tabulator(
            pd.DataFrame(),
            page_size=10,
            sizing_mode='stretch_width',
            theme='modern'
        )
        
        # Log de actividad
        self.log_pane = pn.pane.Markdown(
            "### 📋 Log de Actividad\n\nEsperando acciones...",
            height=200,
            styles={'background': '#f0f0f0', 'padding': '10px'}
        )
    
    def create_empty_chart(self):
        """Crea un gráfico vacío"""
        fig = go.Figure()
        fig.update_layout(
            title="Sin datos disponibles",
            height=300,
            template='plotly_white'
        )
        return fig
    
    def create_layout(self):
        """Organiza el layout del dashboard"""
        
        # Fila de botones
        actions_row = pn.Row(
            self.btn_scan,
            self.btn_refresh,
            pn.layout.HSpacer(),
            self.days_selector
        )
        
        # Fila de indicadores
        stats_row = pn.Row(
            self.card_total_scans,
            self.card_total_findings,
            self.card_high_severity,
            self.card_recent_scans
        )
        
        # Fila de gráficos
        charts_row = pn.Row(
            pn.Column(
                "### 📊 Distribución de Severidad",
                self.severity_chart
            ),
            pn.Column(
                "### 📈 Tendencia Temporal",
                self.trend_chart
            )
        )
        
        # Tabla
        table_section = pn.Column(
            "### 🗃️ Historial de Escaneos",
            self.scans_table
        )
        
        # Layout principal
        self.layout = pn.Column(
            self.title,
            actions_row,
            stats_row,
            charts_row,
            table_section,
            self.log_pane,
            sizing_mode='stretch_width'
        )
    
    def log(self, message):
        """Agrega un mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        current_log = self.log_pane.object
        new_log = f"**[{timestamp}]** {message}\n\n" + current_log
        # Mantener solo últimas 10 líneas
        lines = new_log.split('\n')[:22]  # 10 mensajes * 2 líneas + header
        self.log_pane.object = '\n'.join(lines)
    
    def on_scan_click(self, event):
        """Callback cuando se hace click en ejecutar escaneo"""
        if self.scanning:
            pn.state.notifications.warning('Ya hay un escaneo en curso')
            return
        
        self.scanning = True
        self.btn_scan.loading = True
        self.log("🔍 Iniciando escaneo de red...")
        
        try:
            result = ejecutar_escaneo()
            
            if result and 'error' not in result:
                self.log(f"✅ Escaneo completado: {result['findings']} hallazgos")
                self.log(f"📄 Reportes: {Path(result['csv']).name}")
                pn.state.notifications.success('Escaneo completado exitosamente')
                self.refresh_data()
            else:
                error = result.get('error', 'Error desconocido') if result else 'Sin respuesta'
                self.log(f"❌ Error en escaneo: {error}")
                pn.state.notifications.error(f'Error: {error}')
        except Exception as e:
            self.log(f"❌ Excepción: {str(e)}")
            pn.state.notifications.error(f'Error: {str(e)}')
        finally:
            self.scanning = False
            self.btn_scan.loading = False
    
    def on_refresh_click(self, event):
        """Callback cuando se hace click en refrescar"""
        self.log("🔄 Actualizando datos...")
        self.refresh_data()
        pn.state.notifications.info('Datos actualizados')
    
    def on_days_change(self, event):
        """Callback cuando cambia el selector de días"""
        self.log(f"📅 Cambiando a {event.new} días de tendencia")
        self.update_charts()
    
    def refresh_data(self):
        """Refresca todos los datos del dashboard"""
        if not MODULES_AVAILABLE:
            self.log("⚠️ Módulos no disponibles")
            return
        
        try:
            # Obtener estadísticas
            self.stats = get_statistics()
            
            # Actualizar indicadores
            self.card_total_scans.value = self.stats.get('total_scans', 0)
            self.card_total_findings.value = self.stats.get('total_findings', 0)
            self.card_high_severity.value = self.stats['severity_totals'].get('HIGH', 0)
            self.card_recent_scans.value = self.stats.get('recent_scans', 0)
            
            # Actualizar gráficos
            self.update_charts()
            
            # Actualizar tabla
            self.update_table()
            
            self.log("✅ Datos actualizados correctamente")
        except Exception as e:
            self.log(f"❌ Error actualizando: {str(e)}")
    
    def update_charts(self):
        """Actualiza los gráficos"""
        try:
            days = self.days_selector.value
            
            # Gráfico de severidad (pastel)
            severity_data = self.stats.get('severity_totals', {})
            
            fig_severity = go.Figure(data=[go.Pie(
                labels=['HIGH', 'MEDIUM', 'LOW'],
                values=[
                    severity_data.get('HIGH', 0),
                    severity_data.get('MEDIUM', 0),
                    severity_data.get('LOW', 0)
                ],
                marker=dict(colors=['#dc3545', '#fd7e14', '#ffc107']),
                hole=0.3
            )])
            
            fig_severity.update_layout(
                title=f"Distribución de Severidad",
                height=300,
                template='plotly_white'
            )
            
            self.severity_chart.object = fig_severity
            
            # Gráfico de tendencia temporal
            trends = get_severity_trends(days)
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=trends['dates'],
                y=trends['HIGH'],
                mode='lines+markers',
                name='HIGH',
                line=dict(color='#dc3545', width=2),
                marker=dict(size=6)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=trends['dates'],
                y=trends['MEDIUM'],
                mode='lines+markers',
                name='MEDIUM',
                line=dict(color='#fd7e14', width=2),
                marker=dict(size=6)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=trends['dates'],
                y=trends['LOW'],
                mode='lines+markers',
                name='LOW',
                line=dict(color='#ffc107', width=2),
                marker=dict(size=6)
            ))
            
            fig_trend.update_layout(
                title=f"Tendencia últimos {days} días",
                xaxis_title="Fecha",
                yaxis_title="Cantidad de Hallazgos",
                height=300,
                template='plotly_white',
                hovermode='x unified'
            )
            
            self.trend_chart.object = fig_trend
            
        except Exception as e:
            self.log(f"❌ Error en gráficos: {str(e)}")
    
    def update_table(self):
        """Actualiza la tabla de escaneos"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            scans = get_scans_by_date_range(start_date, end_date)
            
            if scans:
                df = pd.DataFrame([
                    {
                        'ID': s['id'],
                        'Fecha': s['created_at'].strftime('%Y-%m-%d %H:%M') if isinstance(s['created_at'], datetime) else s['created_at'],
                        'Hosts': s['hosts_count'],
                        'Hallazgos': s['findings_count']
                    }
                    for s in scans
                ])
                
                self.scans_table.value = df
            else:
                self.scans_table.value = pd.DataFrame(columns=['ID', 'Fecha', 'Hosts', 'Hallazgos'])
        except Exception as e:
            self.log(f"❌ Error en tabla: {str(e)}")
    
    def view(self):
        """Retorna el layout para servir"""
        return self.layout


# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def create_app():
    """Crea y retorna la aplicación Panel"""
    
    if not MODULES_AVAILABLE:
        return pn.pane.Markdown("""
        # ❌ Error: Módulos no disponibles
        
        Por favor instala las dependencias:
        
        ```bash
        pip install -r requirements.txt
        ```
        """)
    
    dashboard = BlueTeamDashboard()
    return dashboard.view()


# Template personalizado
template = pn.template.FastListTemplate(
    title='BlueTeamBot Lite',
    sidebar=[
        pn.pane.Markdown("""
        ## 🛡️ BlueTeamBot Lite
        
        **Dashboard Interactivo**
        
        ### Características:
        - ▶️ Ejecutar escaneos en vivo
        - 📊 Visualización en tiempo real
        - 📈 Análisis de tendencias
        - 🗃️ Historial completo
        
        ### Uso:
        1. Click en "Ejecutar Escaneo"
        2. Espera los resultados
        3. Explora las gráficas
        4. Revisa el historial
        
        ---
        
        **Versión**: 2.1  
        **Powered by**: Panel + Plotly
        """),
    ],
    main=[create_app()],
    accent_base_color='#1f77b4',
    header_background='#1f77b4',
)

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🛡️  BlueTeamBot Lite - Panel Dashboard")
    print("="*70)
    print("  Iniciando servidor web interactivo...")
    print("  Accede desde: http://localhost:5006")
    print("  Presiona Ctrl+C para detener")
    print("="*70 + "\n")
    
    template.show(port=5006, open=True)
