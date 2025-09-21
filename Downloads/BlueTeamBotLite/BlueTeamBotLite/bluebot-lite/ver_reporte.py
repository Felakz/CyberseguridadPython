import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
import subprocess
from pathlib import Path
import threading
import webbrowser

# Ruta base compatible con script y .exe
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).parent.resolve()

REPORTS_DIR = BASE_DIR / "data" / "reports"
TARGETS_PATH = BASE_DIR / "config" / "targets.yaml"
RULES_PATH = BASE_DIR / "config" / "rules.yaml"

# --- Funciones de negocio ---
def obtener_pdfs():
    return sorted(REPORTS_DIR.glob("report_*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)

def obtener_csvs():
    return sorted(REPORTS_DIR.glob("findings_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)

def abrir_archivo(ruta):
    if not ruta or not Path(ruta).exists():
        messagebox.showerror("Error", f"No se encontró el archivo: {ruta}")
        return
    if sys.platform == "win32":
        os.startfile(str(ruta))
    elif sys.platform == "darwin":
        os.system(f"open '{ruta}'")
    else:
        os.system(f"xdg-open '{ruta}'")

def ejecutar_scan():
    threading.Thread(target=run_scan, daemon=True).start()

def run_scan():
    set_estado("Escaneando...")
    btn_ejecutar.config(state=tk.DISABLED)
    # Evitar ventana de consola extra en Windows
    kwargs = {}
    if sys.platform == "win32":
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    subprocess.run([sys.executable, "-m", "src.main", "--once"], cwd=BASE_DIR, **kwargs)
    actualizar_lista()
    btn_ejecutar.config(state=tk.NORMAL)
    set_estado("Listo. Escaneo finalizado.")
    messagebox.showinfo("Éxito", "Escaneo finalizado y reporte generado.")

def actualizar_lista():
    global pdfs, csvs
    pdfs = obtener_pdfs()
    csvs = obtener_csvs()
    listbox.delete(0, tk.END)
    for pdf in pdfs:
        listbox.insert(tk.END, pdf.name)
    if not pdfs:
        label.config(text="No hay reportes PDF generados.")
    else:
        label.config(text="Selecciona un reporte para abrir:")

def abrir_pdf():
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("Atención", "Selecciona un PDF de la lista.")
        return
    idx = sel[0]
    abrir_archivo(pdfs[idx])

def abrir_csv():
    if not csvs:
        messagebox.showwarning("Atención", "No hay archivos CSV generados.")
        return
    abrir_archivo(csvs[-1])

def abrir_carpeta_reportes():
    ruta = REPORTS_DIR.resolve()
    if sys.platform == "win32":
        os.startfile(str(ruta))
    elif sys.platform == "darwin":
        os.system(f"open '{ruta}'")
    else:
        os.system(f"xdg-open '{ruta}'")

def editar_targets():
    abrir_archivo(TARGETS_PATH)

def editar_rules():
    abrir_archivo(RULES_PATH)

def set_estado(msg):
    estado_var.set(msg)

def salir():
    root.destroy()

def acerca_de():
    messagebox.showinfo("Acerca de", "BlueTeamBot GUI\nDesarrollado con Python y Tkinter\n2025")

def manual_usuario():
    webbrowser.open_new_tab("https://github.com/tu-repo/manual")

# --- Interfaz gráfica ---
root = tk.Tk()
root.title("Visor de Reportes PDF")
root.geometry("500x400")

# Menú superior
menubar = tk.Menu(root)
menu_archivo = tk.Menu(menubar, tearoff=0)
menu_archivo.add_command(label="Ejecutar Escaneo", command=ejecutar_scan)
menu_archivo.add_command(label="Abrir PDF Seleccionado", command=abrir_pdf)
menu_archivo.add_command(label="Abrir CSV más reciente", command=abrir_csv)
menu_archivo.add_separator()
menu_archivo.add_command(label="Abrir carpeta de reportes", command=abrir_carpeta_reportes)
menu_archivo.add_separator()
menu_archivo.add_command(label="Salir", command=salir)
menubar.add_cascade(label="Archivo", menu=menu_archivo)

menu_config = tk.Menu(menubar, tearoff=0)
menu_config.add_command(label="Editar targets.yaml", command=editar_targets)
menu_config.add_command(label="Editar rules.yaml", command=editar_rules)
menubar.add_cascade(label="Configuración", menu=menu_config)

menu_ayuda = tk.Menu(menubar, tearoff=0)
menu_ayuda.add_command(label="Manual de usuario", command=manual_usuario)
menu_ayuda.add_command(label="Acerca de", command=acerca_de)
menubar.add_cascade(label="Ayuda", menu=menu_ayuda)

root.config(menu=menubar)

# Estado
estado_var = tk.StringVar(value="Listo.")
label_estado = tk.Label(root, textvariable=estado_var, anchor="w", fg="blue")
label_estado.pack(fill=tk.X, padx=10, pady=(5,0))

# Lista de PDFs
pdfs = obtener_pdfs()
csvs = obtener_csvs()

label = tk.Label(root, text="Selecciona un reporte para abrir:")
label.pack(padx=10, pady=5)

listbox = tk.Listbox(root, width=50, height=10)
for pdf in pdfs:
    listbox.insert(tk.END, pdf.name)
listbox.pack(padx=10, pady=10)

# Botones
frame = tk.Frame(root)
frame.pack(pady=10)

btn_ejecutar = tk.Button(frame, text="Ejecutar Escaneo", command=ejecutar_scan, width=20)
btn_ejecutar.pack(side=tk.LEFT, padx=10)

btn_abrir = tk.Button(frame, text="Abrir PDF Seleccionado", command=abrir_pdf, width=20)
btn_abrir.pack(side=tk.LEFT, padx=10)

btn_csv = tk.Button(frame, text="Abrir CSV más reciente", command=abrir_csv, width=20)
btn_csv.pack(side=tk.LEFT, padx=10)

btn_carpeta = tk.Button(root, text="Abrir carpeta de reportes", command=abrir_carpeta_reportes)
btn_carpeta.pack(pady=5)

if not pdfs:
    label.config(text="No hay reportes PDF generados.")

root.mainloop()
