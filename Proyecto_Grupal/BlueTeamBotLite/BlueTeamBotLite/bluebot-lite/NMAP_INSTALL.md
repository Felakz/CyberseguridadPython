# 🛡️ BlueTeamBot Lite - Guía de Instalación de nmap

## ❌ Problema Actual
El error `'nmap program was not found in path'` significa que nmap no está accesible desde la línea de comandos.

## ✅ Solución

### Opción 1: Reiniciar Terminal (RÁPIDO)
Ya tienes nmap instalado (v7.97.0), solo necesitas:

1. **Cerrar TODAS las terminales** (PowerShell, CMD, VSCode Terminal)
2. **Abrir PowerShell como Administrador**
3. Ejecutar:
   ```powershell
   nmap --version
   ```
4. Debería mostrar: `Nmap version 7.97.0`

### Opción 2: Agregar al PATH manualmente

1. **Buscar nmap.exe:**
   ```powershell
   Get-ChildItem "C:\ProgramData\chocolatey" -Recurse -Filter "nmap.exe" -ErrorAction SilentlyContinue
   ```

2. **Agregar al PATH de esta sesión:**
   ```powershell
   # Encuentra la ruta (probablemente una de estas):
   $env:Path += ";C:\Program Files (x86)\Nmap"
   # O
   $env:Path += ";C:\ProgramData\chocolatey\lib\nmap\tools"
   
   # Verificar:
   nmap --version
   ```

### Opción 3: Reinstalar nmap

**PowerShell como Administrador:**
```powershell
# Desinstalar
choco uninstall nmap -y

# Reinstalar
choco install nmap -y

# Reiniciar terminal
exit
```

## 🎯 Después de Instalar

Prueba que funciona:
```powershell
nmap --version
nmap localhost
```

## 🔄 Alternativa: Usar Dashboard sin Escaneos

Si quieres solo ver el dashboard con datos de prueba (sin ejecutar escaneos reales):

1. Abre `bluebot_panel.py`
2. El dashboard ya carga datos existentes de la base de datos
3. Solo NO podrás usar el botón "Ejecutar Escaneo"

---

**Última Actualización:** Diciembre 2024
