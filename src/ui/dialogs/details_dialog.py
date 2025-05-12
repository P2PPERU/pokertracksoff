import tkinter as tk
from tkinter import ttk, messagebox
from src.utils.logger import log_message
import pyperclip
from src.core.poker_analyzer import paste_to_poker

def show_details_dialog(parent, entry, config):
    """Muestra un diálogo con los detalles de una entrada del historial"""
    # Extraer datos
    nick = entry.get("nick", "Sin nick")
    timestamp = entry.get("timestamp", "Sin fecha")
    sala = entry.get("sala", "N/A")
    stats = entry.get("stats", "No disponible")
    analysis = entry.get("analisis", "No disponible")
    
    # Crear ventana
    dialog = tk.Toplevel(parent)
    dialog.title(f"Detalles de {nick}")
    dialog.geometry("500x400")
    dialog.minsize(400, 300)
    
    # Frame principal
    frame = ttk.Frame(dialog, padding=10)
    frame.pack(fill="both", expand=True)
    
    # Información básica
    ttk.Label(frame, text=f"Nick: {nick}", font=("Arial", 10, "bold")).pack(anchor="w")
    ttk.Label(frame, text=f"Fecha: {timestamp}").pack(anchor="w")
    ttk.Label(frame, text=f"Sala: {sala}").pack(anchor="w")
    
    # Stats
    ttk.Label(frame, text="Stats:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    stats_text = tk.Text(frame, height=3, wrap="word")
    stats_text.insert("1.0", stats)
    stats_text.config(state="disabled")
    stats_text.pack(fill="x", pady=5)
    
    # Análisis
    ttk.Label(frame, text="Análisis:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    analysis_text = tk.Text(frame, height=15, wrap="word")
    analysis_text.insert("1.0", analysis)
    analysis_text.config(state="disabled")
    analysis_text.pack(fill="both", expand=True, pady=5)
    
    # Frame para botones
    button_frame = ttk.Frame(dialog, padding=10)
    button_frame.pack(fill="x")
    
    # Función para copiar stats
    def copy_stats():
        pyperclip.copy(stats)
        messagebox.showinfo("Copiado", "Stats copiados al portapapeles")
    
    # Función para copiar análisis
    def copy_analysis():
        pyperclip.copy(analysis)
        messagebox.showinfo("Copiado", "Análisis copiado al portapapeles")
    
    # Función para copiar todo
    def copy_all():
        combined = f"{stats}\n{analysis}"
        pyperclip.copy(combined)
        messagebox.showinfo("Copiado", "Contenido completo copiado al portapapeles")
    
    # Función para pegar en mesa
    def paste_to_table():
        # Verificar si hay mesas disponibles
        from src.utils.windows import find_poker_tables
        tables = find_poker_tables()
        
        if not tables:
            messagebox.showwarning("Error", "No se encontraron mesas de poker abiertas")
            return
        
        # Preguntar qué pegar
        dialog_result = messagebox.askquestion(
            "Pegar en mesa",
            "¿Qué quieres pegar en la mesa activa?",
            type="yesnocancel"
        )
        
        # Determinar qué pegar según respuesta
        if dialog_result == "yes":  # Sí = Stats
            content = stats
        elif dialog_result == "no":  # No = Análisis
            content = analysis
        else:  # Cancel o cierre = Ambos
            content = f"{stats}\n{analysis}"
        
        # Pegar el contenido seleccionado
        if content:
            log_message(f"Pegando en mesa: {content[:30]}...")
            paste_to_poker(content)
    
    # Botones de acción
    ttk.Button(button_frame, text="Copiar Stats", command=copy_stats).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Copiar Análisis", command=copy_analysis).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Copiar Todo", command=copy_all).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Pegar en Mesa", command=paste_to_table).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Cerrar", command=dialog.destroy).pack(side="right", padx=5)
    
    # Centrar ventana
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    # Intentar añadir ícono
    try:
        dialog.iconbitmap("assets/icon.ico")
    except:
        pass
    
    # Hacer que el diálogo sea modal
    dialog.transient(parent)
    dialog.grab_set()
    parent.wait_window(dialog)