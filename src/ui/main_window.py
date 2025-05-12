import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading

from src.utils.logger import log_message, get_logger
from src.utils.windows import get_window_under_cursor, find_poker_tables
from src.core.poker_analyzer import analyze_table
from src.ui.tabs.main_tab import create_main_tab
from src.ui.tabs.history_tab import create_history_tab
from src.ui.tabs.config_tab import create_config_tab
from src.ui.tabs.logs_tab import create_logs_tab

# Variables globales de la UI
root = None
tab_control = None
history_tree = None
running = True
auto_running = False

def create_main_window(config):
    """Crea la ventana principal de la aplicación"""
    global root, tab_control, running
    
    # Crear ventana principal
    root = tk.Tk()
    root.title("PokerBot Pro")
    root.geometry("800x600")
    root.minsize(600, 400)
    
    # Configurar tema
    setup_theme(config["tema"])
    
    # Crear pestañas
    tab_control = ttk.Notebook(root)
    
    # Pestaña Principal
    main_tab = create_main_tab(tab_control, config)
    tab_control.add(main_tab, text='Principal')
    
    # Pestaña Historial
    history_tab, history_tree = create_history_tab(tab_control, config)
    tab_control.add(history_tab, text='Historial')
    
    # Pestaña Configuración
    config_tab = create_config_tab(tab_control, config)
    tab_control.add(config_tab, text='Configuración')
    
    # Pestaña Logs
    logs_tab = create_logs_tab(tab_control)
    tab_control.add(logs_tab, text='Logs')
    
    # Empaquetar pestañas
    tab_control.pack(expand=1, fill="both")
    
    # Registrar hotkey
    try:
        keyboard.add_hotkey(config["hotkey"], lambda: hotkey_handler(config))
        log_message(f"Hotkey {config['hotkey']} registrada correctamente")
    except Exception as e:
        log_message(f"Error al registrar hotkey: {e}", level='error')
    
    # Configurar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Iniciar modo automático si está configurado
    if config["modo_automatico"]:
        root.after(1000, lambda: start_auto_mode(config))
    
    # Bienvenida
    log_message("=== PokerBot Pro iniciado correctamente ===")
    log_message(f"Presiona {config['hotkey']} o haz clic derecho para analizar nick")
    
    # Iniciar bucle de eventos
    root.mainloop()

def setup_theme(theme_name):
    """Configura el tema de la aplicación"""
    theme_colors = {
        "dark": {
            "bg": "#2d2d30",
            "fg": "#ffffff",
            "btn_bg": "#007acc",
            "btn_fg": "#ffffff",
            "input_bg": "#3e3e42",
            "input_fg": "#ffffff",
            "tree_bg": "#252526",
            "tree_fg": "#ffffff",
            "tab_bg": "#2d2d30",
            "tab_fg": "#ffffff",
            "highlight_bg": "#3e3e42"
        },
        "light": {
            "bg": "#f0f0f0",
            "fg": "#000000",
            "btn_bg": "#007acc",
            "btn_fg": "#ffffff",
            "input_bg": "#ffffff",
            "input_fg": "#000000",
            "tree_bg": "#ffffff",
            "tree_fg": "#000000",
            "tab_bg": "#f0f0f0",
            "tab_fg": "#000000",
            "highlight_bg": "#e0e0e0"
        }
    }
    
    current_theme = theme_colors.get(theme_name, theme_colors["dark"])
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')
    
    # Aplicar colores
    style.configure('TFrame', background=current_theme["bg"])
    style.configure('TLabel', background=current_theme["bg"], foreground=current_theme["fg"])
    style.configure('TButton', background=current_theme["btn_bg"], foreground=current_theme["btn_fg"])
    style.configure('TEntry', fieldbackground=current_theme["input_bg"], foreground=current_theme["input_fg"])
    style.configure('TNotebook', background=current_theme["tab_bg"])
    style.configure('TNotebook.Tab', background=current_theme["tab_bg"], foreground=current_theme["tab_fg"])
    style.map('TNotebook.Tab', background=[('selected', current_theme["highlight_bg"])])
    style.configure('Treeview', 
                    background=current_theme["tree_bg"],
                    foreground=current_theme["tree_fg"],
                    fieldbackground=current_theme["tree_bg"])

def hotkey_handler(config):
    """Maneja la activación del hotkey global"""
    hwnd, title = get_window_under_cursor()
    if hwnd:
        threading.Thread(target=analyze_table, args=(hwnd, config, None, False)).start()
    else:
        # Sin mesa específica, buscar la primera disponible
        tables = find_poker_tables()
        if tables:
            hwnd, title = tables[0]
            threading.Thread(target=analyze_table, args=(hwnd, config, None, False)).start()
        else:
            log_message("No se encontró ninguna mesa activa", level='warning')

def start_auto_mode(config):
    """Inicia el modo automático"""
    global auto_running
    
    if auto_running:
        log_message("El modo automático ya está en ejecución")
        return
    
    auto_running = True
    threading.Thread(target=auto_mode_loop, args=(config,), daemon=True).start()
    log_message("Modo automático iniciado")
    update_ui_status()

def stop_auto_mode():
    """Detiene el modo automático"""
    global auto_running
    
    if not auto_running:
        log_message("El modo automático no está en ejecución")
        return
    
    auto_running = False
    log_message("Deteniendo modo automático...")
    update_ui_status()

def auto_mode_loop(config):
    """Bucle principal del modo automático"""
    global auto_running, running
    
    log_message("Iniciando bucle automático")
    
    while auto_running and running:
        try:
            tables = find_poker_tables()
            if tables:
                for hwnd, title in tables:
                    if not auto_running:
                        break
                    
                    log_message(f"Procesando mesa: {title}")
                    analyze_table(hwnd, config)
                    time.sleep(1)  # Pausa entre mesas
            
            # Esperar antes de siguiente ciclo
            for _ in range(config["auto_check_interval"]):
                if not auto_running:
                    break
                time.sleep(1)
        except Exception as e:
            log_message(f"Error en bucle automático: {e}", level='error')
            time.sleep(5)
    
    log_message("Bucle automático finalizado")

def update_ui_status():
    """Actualiza el estado en la UI"""
    if not root or not root.winfo_ismapped():
        return
    
    try:
        for tab in tab_control.winfo_children():
            if hasattr(tab, 'winfo_name') and tab.winfo_name() == "main_tab":
                for frame in tab.winfo_children():
                    if isinstance(frame, ttk.Frame) and hasattr(frame, 'winfo_name') and frame.winfo_name() == "status_frame":
                        for widget in frame.winfo_children():
                            # Actualizar botón de modo automático
                            if hasattr(widget, 'cget') and widget.cget('text') in ["Iniciar modo automático", "Detener modo automático"]:
                                widget.config(
                                    text="Detener modo automático" if auto_running else "Iniciar modo automático",
                                    command=stop_auto_mode if auto_running else lambda: start_auto_mode(get_current_config())
                                )
                            
                            # Actualizar etiqueta de estado
                            if hasattr(widget, 'cget') and widget.cget('text') == "Estado:":
                                next_idx = frame.winfo_children().index(widget) + 1
                                if next_idx < len(frame.winfo_children()):
                                    status_label = frame.winfo_children()[next_idx]
                                    if hasattr(status_label, 'config'):
                                        status_label.config(
                                            text="Activo" if auto_running else "Inactivo",
                                            foreground="green" if auto_running else "red"
                                        )
    except Exception as e:
        log_message(f"Error al actualizar UI: {e}", level='error')

def get_current_config():
    """Obtiene la configuración actual desde las pestañas de UI"""
    from src.config.settings import load_config
    # Recargar configuración del archivo para obtener cambios recientes
    return load_config()

def on_closing():
    """Maneja el cierre de la aplicación"""
    global running, auto_running
    
    if messagebox.askokcancel("Salir", "¿Estás seguro de querer salir?"):
        # Detener procesos en segundo plano
        running = False
        auto_running = False
        
        # Destruir ventana
        root.destroy()