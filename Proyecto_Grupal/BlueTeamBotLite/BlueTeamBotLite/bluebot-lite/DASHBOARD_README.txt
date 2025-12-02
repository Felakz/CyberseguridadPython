================================================================================
                 DASHBOARD WEB - GUÍA DE INICIO RÁPIDO
================================================================================

¡FELICIDADES! El dashboard web está completamente implementado.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASO 1: INICIAR EL DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Abrir PowerShell y ejecutar:

    cd c:\Users\DARIO\Desktop\Proyecto_Grupal\BlueTeamBotLite\BlueTeamBotLite\bluebot-lite
    ..\.venv\Scripts\python.exe dashboard_web.py

Verás el mensaje:
    ======================================================================
      BlueTeamBot Dashboard Web - Iniciando...
    ======================================================================
      Accede desde: http://localhost:5000
      Presiona Ctrl+C para detener
    ======================================================================


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PASO 2: ABRIR EN NAVEGADOR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

En Chrome, Firefox o Edge:
    http://localhost:5000

Desde otros dispositivos en tu red:
    http://[TU-IP]:5000


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUNCIONALIDADES DISPONIBLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 DASHBOARD PRINCIPAL (/)
   ✓ 4 tarjetas con métricas clave
   ✓ Gráfico de tendencias (30 días)
   ✓ Gráfico de pastel (distribución)
   ✓ Botones de acceso rápido

📈 ESTADÍSTICAS (/estadisticas)
   ✓ Tabla resumen general
   ✓ Cards grandes por severidad
   ✓ Números históricos completos

📉 TENDENCIAS (/tendencias)
   ✓ Selector de período (7/30/60/90 días)
   ✓ Gráfico global de evolución
   ✓ Gráficos individuales por host

🔄 COMPARAR (/comparar)
   ✓ Selectores de fechas para 2 períodos
   ✓ Comparativa visual con deltas
   ✓ Top 5 hosts de cada período
   ✓ Alertas de mejora/empeoramiento

📋 HISTORIAL (/scans)
   ✓ Tabla de todos los escaneos
   ✓ Filtro por período
   ✓ Modal con detalles completos


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API REST DISPONIBLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GET /api/stats
    Devuelve estadísticas generales

GET /api/severity-trends?days=30
    Devuelve tendencias de severidad

GET /api/host-trends?days=30
    Devuelve tendencias por host

GET /api/scans?days=30
    Devuelve lista de escaneos

GET /api/scan/{id}/findings
    Devuelve detalles de un escaneo

POST /api/compare
    Body: {
        "range1_start": "2025-11-01T00:00:00",
        "range1_end": "2025-11-15T23:59:59",
        "range2_start": "2025-11-16T00:00:00",
        "range2_end": "2025-11-30T23:59:59"
    }


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVOS CREADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ dashboard_web.py          - Servidor Flask
✅ templates/base.html        - Plantilla base
✅ templates/index.html       - Dashboard principal
✅ templates/stats.html       - Estadísticas
✅ templates/tendencias.html  - Análisis de tendencias
✅ templates/comparar.html    - Comparativa
✅ templates/scans.html       - Historial
✅ static/css/style.css       - Estilos personalizados
✅ static/js/charts.js        - Utilidades de gráficos
✅ requirements.txt           - Actualizado con Flask


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TECNOLOGÍAS UTILIZADAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend:
  ✓ Flask 3.1.2 (framework web)
  ✓ SQLAlchemy 2.0.44 (ORM)
  ✓ Python 3.13

Frontend:
  ✓ Bootstrap 5.3 (diseño responsive)
  ✓ Chart.js 4.4 (gráficos interactivos)
  ✓ Bootstrap Icons (iconografía)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTAS IMPORTANTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Para ver datos en el dashboard, primero debes:
    1. Ejecutar al menos un escaneo (ejecutar.bat)
    2. La base de datos debe tener registros

💡  El dashboard se actualiza automáticamente al cargar las páginas

🔒  El dashboard NO tiene autenticación por defecto
    - Solo usar en redes internas confiables
    - O agregar autenticación Flask-Login si es necesario

🌐  Requiere conexión a internet para:
    - Bootstrap CSS/JS (CDN)
    - Chart.js (CDN)
    - Bootstrap Icons (CDN)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SIGUIENTE PASO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 TODO LISTO: Ejecuta el dashboard y explora las visualizaciones!

📖 Documentación completa actualizada en: MANUAL_USUARIO.txt

================================================================================
