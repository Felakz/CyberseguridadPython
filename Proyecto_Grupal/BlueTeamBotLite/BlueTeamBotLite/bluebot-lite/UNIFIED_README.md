# 🛡️ BlueTeamBot Unified - Guía Rápida

## 📦 ¿Qué es bluebot_unified.py?

Un **solo archivo Python** que integra:
- ✅ Escáner de red (nmap)
- ✅ Dashboard web (Flask)
- ✅ Menú interactivo
- ✅ Base de datos SQLite
- ✅ Reportes PDF/CSV

---

## 🚀 Formas de Uso

### 1️⃣ Menú Interactivo (RECOMENDADO para principiantes)

```bash
python bluebot_unified.py
```

**Se mostrará:**
```
══════════════════════════════════════════════════════════════════════
  🛡️  BlueTeamBot Lite - Aplicación Unificada
══════════════════════════════════════════════════════════════════════

  Selecciona una opción:

  [1] 🔍 Ejecutar Escaneo de Red
  [2] 🌐 Iniciar Dashboard Web
  [3] 🚀 Escanear y luego Iniciar Dashboard
  [4] ❌ Salir

══════════════════════════════════════════════════════════════════════
```

**Opción 1**: Ejecuta un escaneo completo y genera reportes  
**Opción 2**: Inicia solo el dashboard web en http://localhost:5000  
**Opción 3**: Primero escanea (actualiza datos) y luego abre dashboard  
**Opción 4**: Salir del programa

---

### 2️⃣ Línea de Comandos (Para automatización)

#### Solo ejecutar escaneo:
```bash
python bluebot_unified.py --scan
```

#### Solo iniciar dashboard:
```bash
python bluebot_unified.py --dashboard
```

#### Escanear Y luego dashboard (automatizado):
```bash
python bluebot_unified.py --scan-and-serve
```

#### Dashboard en puerto personalizado:
```bash
python bluebot_unified.py --dashboard --port 8080
```

#### Ver todas las opciones:
```bash
python bluebot_unified.py --help
```

---

## 🎯 Casos de Uso Comunes

### Para operaciones diarias:
```bash
# Opción rápida con menú
python bluebot_unified.py
# Selecciona [3] para escanear y ver resultados
```

### Para scripts automatizados:
```bash
# Escaneo nocturno automático
python bluebot_unified.py --scan
```

### Para presentaciones/demostraciones:
```bash
# Escanea primero (datos frescos) y luego muestra dashboard
python bluebot_unified.py --scan-and-serve
```

### Para acceso remoto:
```bash
# Permite acceso desde otras PCs en la red
python bluebot_unified.py --dashboard --host 0.0.0.0 --port 5000
# Accede desde: http://IP-SERVIDOR:5000
```

---

## 📊 Ventajas vs Archivos Separados

| Característica | bluebot_unified.py | Archivos separados |
|---------------|--------------------|--------------------|
| **Simplicidad** | ✅ 1 solo archivo | ❌ 3 archivos diferentes |
| **Menú interactivo** | ✅ Sí | ❌ No |
| **Escaneo desde web** | ✅ Endpoint /api/scan/run | ❌ No disponible |
| **Modo combinado** | ✅ --scan-and-serve | ❌ Hay que ejecutar 2 veces |
| **Distribución** | ✅ Copiar 1 archivo | ❌ Copiar proyecto completo |

---

## 🔧 Argumentos Disponibles

```
python bluebot_unified.py [OPCIONES]

Opciones:
  --scan, -s              Solo escaneo de red
  --dashboard, -d         Solo dashboard web
  --scan-and-serve, -ss   Escaneo + Dashboard automático
  --port PUERTO, -p       Puerto del dashboard (default: 5000)
  --host IP               IP donde escuchar (default: 0.0.0.0)
  --no-debug              Desactivar modo debug de Flask
  --help, -h              Mostrar ayuda
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: Primera vez usando la herramienta
```bash
python bluebot_unified.py
# Selecciona [3] para escanear y ver dashboard con datos
```

### Ejemplo 2: Agregar a tareas programadas (Windows)
```powershell
# Crear tarea que ejecuta escaneo diario a las 2 AM
schtasks /create /tn "BlueBot Scan" /tr "python C:\ruta\bluebot_unified.py --scan" /sc daily /st 02:00
```

### Ejemplo 3: Dashboard permanente en servidor
```bash
# Iniciar dashboard en modo producción (sin debug)
python bluebot_unified.py --dashboard --no-debug --port 80
```

### Ejemplo 4: Escaneo y envío de resultados
```bash
# Script que escanea y envía email con resultados
python bluebot_unified.py --scan && python enviar_email.py
```

---

## ⚙️ Requisitos

- Python 3.8+
- nmap instalado en el sistema
- Dependencias: `pip install -r requirements.txt`
- Configuración: Editar `config/targets.yaml` y `config/rules.yaml`

---

## 🆚 ¿Cuándo usar cada archivo?

### Usar `bluebot_unified.py` cuando:
- ✅ Necesitas simplicidad y rapidez
- ✅ Quieres un menú interactivo
- ✅ Vas a distribuir la herramienta a otros usuarios
- ✅ Prefieres un solo comando para todo
- ✅ Quieres ejecutar escaneos desde el navegador

### Usar archivos separados cuando:
- ❌ Necesitas ejecutar SOLO el dashboard sin código de escaneo
- ❌ Tienes limitaciones de memoria (archivo más pequeño)
- ❌ Quieres personalizar profundamente cada componente

---

## 🐛 Solución de Problemas

**Error: ModuleNotFoundError**
```bash
# Instalar dependencias
pip install -r requirements.txt
```

**Error: nmap no encontrado**
```bash
# Windows: Descargar desde https://nmap.org/download.html
# Linux: sudo apt install nmap
```

**Puerto 5000 en uso**
```bash
# Usar otro puerto
python bluebot_unified.py --dashboard --port 8080
```

**No se ven datos en dashboard**
```bash
# Primero ejecuta un escaneo
python bluebot_unified.py --scan
# Luego inicia dashboard
python bluebot_unified.py --dashboard
```

---

## 📞 Ayuda Adicional

Para documentación completa, consulta: **MANUAL_USUARIO.txt**

Para ver el historial de mejoras: **MEJORAS_IMPLEMENTADAS.md**

---

**Última actualización**: Diciembre 2024  
**Versión**: 2.1 (Unified Release)
