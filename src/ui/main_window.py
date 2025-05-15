import tkinter as tk
import threading
import time

# Inicializar variables globales
USING_TTKBOOTSTRAP = False
ttk = None

# Intentar usar el módulo de compatibilidad
try:
    from src.utils.ttkbootstrap_compat import (
        ttk, USING_TTKBOOTSTRAP, FALLBACK_MODE, 
        init_ttkbootstrap, create_themed_button, create_themed_label,
        apply_theme_to_toplevel, COLORS, apply_global_dark_theme
    )
    print("Usando módulo de compatibilidad ttkbootstrap_compat en main_window.py")
except ImportError:
    # Si no está disponible el módulo de compatibilidad, usar la detección estándar
    try:
        import sys
        import importlib.util
        
        # Verificar si ttkbootstrap está instalado correctamente
        ttk_spec = importlib.util.find_spec("ttkbootstrap")
        if ttk_spec is not None:
            import ttkbootstrap
            from ttkbootstrap.style import Style
            import ttkbootstrap as ttk
            from ttkbootstrap.constants import *
            USING_TTKBOOTSTRAP = True
            try:
                version_info = ttkbootstrap.__version__
            except AttributeError:
                try:
                    if hasattr(ttkbootstrap, 'VERSION'):
                        version_info = ttkbootstrap.VERSION
                    else:
                        version_info = "desconocida"
                except:
                    version_info = "desconocida"
            print(f"ttkbootstrap inicializado correctamente (versión {version_info})")
        else:
            from tkinter import ttk
            print("ttkbootstrap no está instalado, usando ttk estándar")
    except Exception as e:
        print(f"Error al importar ttkbootstrap: {e}")
        from tkinter import ttk
        print("ttkbootstrap no está disponible, usando ttk estándar")

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
history_treeview = None  # Referencia global al treeview del historial
running = True
auto_running = False

def setup_scrolling(tab):
    """Configura el desplazamiento correcto para una pestaña"""
    canvas = tk.Canvas(tab)
    scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    # Binds para que el scroll funcione
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.bind("<Configure>", 
               lambda e: canvas.itemconfig("window", width=e.width))
    
    # Binds para scroll con el ratón - MEJORADO
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    # Asegurarse de que el binding sea global para que funcione al pasar sobre cualquier widget hijo
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Función para limpiar el binding cuando se destruya el canvas
    def _on_destroy(event):
        try:
            canvas.unbind_all("<MouseWheel>")
        except:
            pass
    
    canvas.bind("<Destroy>", _on_destroy)
    
    # Crear ventana dentro del canvas
    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="window")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Empaquetar todo
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return scrollable_frame

def create_main_window(config):
    """Crea la ventana principal de la aplicación"""
    global root, tab_control, history_treeview, running, USING_TTKBOOTSTRAP
    
    try:
        # Determinar tema
        is_dark = config["tema"] == "dark"
        
        # Intentar usar el módulo de compatibilidad para crear la ventana
        try:
            from src.utils.ttkbootstrap_compat import create_root_window, apply_global_dark_theme
            theme = "darkly" if is_dark else "cosmo"
            root = create_root_window(title="PokerBot TRACK", theme=theme, size="900x650")
            log_message("Ventana creada con el módulo de compatibilidad")
            
            # Aplicar tema global oscuro si es necesario
            if is_dark:
                try:
                    apply_global_dark_theme()
                except Exception as e:
                    log_message(f"Error al aplicar tema oscuro global: {e}", level='debug')
                
                # Forzar colores oscuros en la raíz
                root.configure(bg="#2d2d30")
                
        except ImportError:
            # Si no está disponible, usar el método estándar
            # Crea un sistema antiduplicación para que ttkbootstrap no genere error
            tk._default_root = None
            
            try:
                if USING_TTKBOOTSTRAP:
                    # Asegurarse de que no hay una raíz existente
                    tk._default_root = None
                    
                    # Crear un estilo sin inicializar scrollbars o comboboxes primero
                    theme = "darkly" if is_dark else "cosmo"
                    style = Style(theme=theme)
                    root = style.master
                else:
                    root = tk.Tk()
                    
                    # Si es tema oscuro y no tenemos ttkbootstrap, aplicar manualmente
                    if is_dark:
                        # Aplicar colores oscuros manualmente
                        root.configure(bg="#2d2d30")
                        
                        # Configurar estilo para todos los widgets
                        style = ttk.Style()
                        
                        # Definir colores oscuros
                        dark_bg = "#2d2d30"
                        dark_fg = "#ffffff"
                        
                        # Configurar widgets básicos
                        style.configure("TFrame", background=dark_bg)
                        style.configure("TLabel", background=dark_bg, foreground=dark_fg)
                        style.configure("TButton", background="#007acc")
                        style.configure("TNotebook", background=dark_bg)
                        style.configure("TNotebook.Tab", background="#3e3e42", foreground=dark_fg)
                        style.map("TNotebook.Tab", background=[("selected", "#007acc")], 
                                 foreground=[("selected", "white")])
                        
                        # Configuración global
                        style.configure(".", 
                                      background=dark_bg,
                                      foreground=dark_fg,
                                      fieldbackground=dark_bg,
                                      troughcolor="#3e3e42",
                                      darkcolor="#3e3e42",
                                      lightcolor="#007acc")
                        
                        # Treeview
                        style.configure("Treeview", 
                                      background=dark_bg,
                                      foreground=dark_fg,
                                      fieldbackground=dark_bg)
                        style.configure("Treeview.Heading", 
                                      background="#3e3e42",
                                      foreground=dark_fg)
                        style.map("Treeview", 
                                background=[("selected", "#007acc")],
                                foreground=[("selected", "white")])
            except Exception as e:
                log_message(f"Error al crear ventana principal: {e}", level='warning')
                # Fallback
                root = tk.Tk()
                USING_TTKBOOTSTRAP = False
            
            root.title("PokerPRO TRACK")
            root.geometry("900x650")
        
        # Configuración común de la ventana
        root.minsize(700, 500)
        
        # Ícono de la aplicación
        try:
            root.iconphoto(True, tk.PhotoImage(file="assets/icon.png"))
        except Exception as e:
            log_message(f"No se pudo cargar el ícono: {e}", level='debug')
        
        # Crear pestañas
        tab_control = ttk.Notebook(root)
        
        # Aplicar estilos para tema oscuro si es necesario
        if is_dark and not USING_TTKBOOTSTRAP:
            style = ttk.Style()
            style.configure("TNotebook", background="#2d2d30")
            style.configure("TNotebook.Tab", background="#3e3e42", foreground="white")
            style.map("TNotebook.Tab", background=[("selected", "#007acc")], 
                     foreground=[("selected", "white")])
        
        # Pestaña Principal (uso try/except para cada pestaña para que el error en una no afecte a las demás)
        try:
            main_tab = create_main_tab(tab_control, config)
            tab_control.add(main_tab, text='Principal')
        except Exception as e:
            log_message(f"Error al crear pestaña Principal: {e}", level='error')
            import traceback
            log_message(traceback.format_exc(), level='debug')
            # Crear una pestaña vacía como fallback
            fallback_tab = ttk.Frame(tab_control)
            ttk.Label(fallback_tab, text="Error al cargar pestaña Principal").pack(pady=20)
            tab_control.add(fallback_tab, text='Principal')
        
        # Pestaña Historial
        try:
            history_tab, history_tree = create_history_tab(tab_control, config)
            tab_control.add(history_tab, text='Historial')
            
            # Guardar referencia global al treeview de historial
            history_treeview = history_tree
        except Exception as e:
            log_message(f"Error al crear pestaña Historial: {e}", level='error')
            fallback_tab = ttk.Frame(tab_control)
            ttk.Label(fallback_tab, text="Error al cargar pestaña Historial").pack(pady=20)
            tab_control.add(fallback_tab, text='Historial')
        
        # Pestaña Configuración
        try:
            config_tab = create_config_tab(tab_control, config)
            tab_control.add(config_tab, text='Configuración')
        except Exception as e:
            log_message(f"Error al crear pestaña Configuración: {e}", level='error')
            fallback_tab = ttk.Frame(tab_control)
            ttk.Label(fallback_tab, text="Error al cargar pestaña Configuración").pack(pady=20)
            tab_control.add(fallback_tab, text='Configuración')
        
        # Pestaña Logs
        try:
            logs_tab = create_logs_tab(tab_control)
            tab_control.add(logs_tab, text='Logs')
        except Exception as e:
            log_message(f"Error al crear pestaña Logs: {e}", level='error')
            fallback_tab = ttk.Frame(tab_control)
            ttk.Label(fallback_tab, text="Error al cargar pestaña Logs").pack(pady=20)
            tab_control.add(fallback_tab, text='Logs')
        
        # Barra de estado - usar métodos del módulo de compatibilidad si está disponible
        try:
            if USING_TTKBOOTSTRAP:
                try:
                    from src.utils.ttkbootstrap_compat import create_themed_frame
                    status_bar = create_themed_frame(root, "secondary")
                except ImportError:
                    status_bar = ttk.Frame(root, bootstyle="secondary")
            else:
                status_bar = ttk.Frame(root)
                if is_dark:
                    status_bar.configure(style="TFrame")
        except Exception:
            status_bar = ttk.Frame(root)
            
        status_bar.pack(side="bottom", fill="x")
        
        status_label = ttk.Label(status_bar, text="Listo", padding=5)
        status_label.pack(side="left")
        
        version_label = ttk.Label(status_bar, text="PokerBot Pro v1.0", padding=5)
        version_label.pack(side="right")
        
        # Empaquetar pestañas
        tab_control.pack(expand=1, fill="both", padx=5, pady=5)
        
        # Registrar hotkey
        try:
            import keyboard
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
        
    except Exception as e:
        log_message(f"Error al crear la interfaz con ttkbootstrap: {e}", level='critical')
        import traceback
        log_message(traceback.format_exc(), level='critical')
        # Si falla ttkbootstrap, intentamos con la interfaz básica
        fallback_interface(config)

def fallback_interface(config):
    """Interfaz básica en caso de error con ttkbootstrap"""
    global root, tab_control, running, history_treeview
    
    try:
        log_message("Iniciando interfaz de respaldo sin ttkbootstrap")
        # Usar tkinter estándar
        root = tk.Tk()
        root.title("PokerPRO TRACKo (Modo compatible)")
        root.geometry("800x600")
        
        # Configurar estilo
        style = ttk.Style()
        if config["tema"] == "dark":
            root.configure(bg="#333")
            style.configure("TFrame", background="#333")
            style.configure("TLabel", background="#333", foreground="white")
        
        # Mensaje informativo
        message_label = tk.Label(
            root, 
            text="Modo de compatibilidad activado. Se recomienda reinstalar ttkbootstrap.\nLa aplicación funciona pero con interfaz básica.", 
            bg="#333" if config["tema"] == "dark" else "#f0f0f0",
            fg="white" if config["tema"] == "dark" else "black",
            font=("Arial", 10, "bold")
        )
        message_label.pack(pady=10)
        
        # Crear pestañas simplificadas pero funcionales
        tab_control = ttk.Notebook(root)
        
        # Crear pestañas básicas para funcionalidad mínima
        main_tab = ttk.Frame(tab_control)
        
        # Añadir elementos básicos a la pestaña principal
        search_frame = ttk.Frame(main_tab, padding=10)
        search_frame.pack(fill="x", pady=10)
        
        ttk.Label(search_frame, text="Buscar nick:").grid(row=0, column=0, padx=5, pady=5)
        entry_nick = ttk.Entry(search_frame, width=20)
        entry_nick.grid(row=0, column=1, padx=5, pady=5)
        
        # Función de búsqueda simple
        def simple_search():
            nick = entry_nick.get().strip()
            if not nick:
                # Asegurar que messagebox esté importado
                from tkinter import messagebox
                messagebox.showwarning("Campo vacío", "Ingresa un nick para buscar")
                return
                
            tables = find_poker_tables()
            if tables:
                hwnd, _ = tables[0]
                threading.Thread(target=analyze_table, args=(hwnd, config, nick, True)).start()
            else:
                from tkinter import messagebox
                messagebox.showwarning("Sin mesa", "No se encontró una mesa de poker activa")
        
        ttk.Button(search_frame, text="Buscar", command=simple_search).grid(row=0, column=2, padx=5, pady=5)
        
        # Botón para modo automático
        auto_frame = ttk.Frame(main_tab, padding=10)
        auto_frame.pack(fill="x", pady=10)
        
        def toggle_auto_mode():
            global auto_running
            if auto_running:
                stop_auto_mode()
                auto_btn.config(text="Iniciar modo automático")
            else:
                start_auto_mode(config)
                auto_btn.config(text="Detener modo automático")
        
        auto_btn = ttk.Button(auto_frame, text="Iniciar modo automático" if not auto_running else "Detener modo automático", 
                             command=toggle_auto_mode)
        auto_btn.pack(pady=5)
        
        # Añadir pestañas
        tab_control.add(main_tab, text='Principal')
        
        # Historial simple
        history_tab = ttk.Frame(tab_control)
        history_tree = ttk.Treeview(history_tab, columns=("fecha", "nick", "sala", "stats"), show="headings", height=10)
        history_tree.heading("fecha", text="Fecha")
        history_tree.heading("nick", text="Nick")
        history_tree.heading("sala", text="Sala")
        history_tree.heading("stats", text="Stats")
        
        # Guardar referencia
        history_treeview = history_tree
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_tab, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        history_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Cargar historial
        from src.ui.tabs.history_tab import update_history_treeview
        update_history_treeview(history_tree)
        
        tab_control.add(history_tab, text='Historial')
        
        # Pestañas de configuración y logs (simples)
        config_tab = ttk.Frame(tab_control)
        ttk.Label(config_tab, text="La configuración completa está disponible al reinstalar ttkbootstrap").pack(pady=20)
        tab_control.add(config_tab, text='Configuración')
        
        logs_tab = ttk.Frame(tab_control)
        log_text = tk.Text(logs_tab, wrap="word", height=20)
        log_text.pack(fill="both", expand=True, padx=10, pady=10)
        tab_control.add(logs_tab, text='Logs')
        
        tab_control.pack(expand=1, fill="both")
        
        # Registrar hotkey
        try:
            import keyboard
            keyboard.add_hotkey(config["hotkey"], lambda: hotkey_handler(config))
        except Exception as e:
            log_message(f"Error al registrar hotkey en interfaz de respaldo: {e}", level='warning')
        
        # Configurar cierre
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar modo automático si está configurado
        if config["modo_automatico"]:
            root.after(1000, lambda: start_auto_mode(config))
        
        root.mainloop()
    except Exception as e:
        log_message(f"Error crítico en interfaz de respaldo: {e}", level='critical')
        import traceback
        log_message(traceback.format_exc(), level='critical')
        from tkinter import messagebox
        messagebox.showerror("Error crítico", 
                             "No se pudo iniciar la interfaz. Reinstala las dependencias y vuelve a intentarlo.")

def setup_theme(theme_name):
    """Configurar tema personalizado (ahora gestionado por ttkbootstrap)"""
    # Esta función se mantiene por compatibilidad pero no hace nada
    pass

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
            if root and root.winfo_exists():
                # Usar el módulo de compatibilidad si está disponible
                try:
                    from src.utils.ttkbootstrap_compat import show_message
                    show_message("Sin mesa", "No se encontró ninguna mesa de poker activa", "warning")
                except ImportError:
                    # Fallback al método estándar
                    try:
                        if USING_TTKBOOTSTRAP:
                            try:
                                from ttkbootstrap.dialogs import Messagebox
                                Messagebox.show_warning("Sin mesa", "No se encontró ninguna mesa de poker activa")
                            except:
                                from tkinter import messagebox
                                messagebox.showwarning("Sin mesa", "No se encontró ninguna mesa de poker activa")
                        else:
                            from tkinter import messagebox
                            messagebox.showwarning("Sin mesa", "No se encontró ninguna mesa de poker activa")
                    except:
                        from tkinter import messagebox
                        messagebox.showwarning("Sin mesa", "No se encontró ninguna mesa de poker activa")

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
    
    # Mostrar notificación usando el módulo de compatibilidad si está disponible
    try:
        from src.utils.ttkbootstrap_compat import show_toast
        show_toast("Modo Automático", "Modo automático iniciado", "success")
    except ImportError:
        # Fallback
        if root and root.winfo_exists() and USING_TTKBOOTSTRAP:
            try:
                from ttkbootstrap.toast import ToastNotification
                ToastNotification(
                    title="Modo Automático",
                    message="Modo automático iniciado",
                    duration=3000,
                    bootstyle="success"
                ).show_toast()
            except Exception as e:
                log_message(f"Error al mostrar notificación: {e}", level='debug')
                try:
                    from tkinter import messagebox
                    messagebox.showinfo("Modo Automático", "Modo automático iniciado")
                except:
                    pass

def stop_auto_mode():
    """Detiene el modo automático"""
    global auto_running
    
    if not auto_running:
        log_message("El modo automático no está en ejecución")
        return
    
    auto_running = False
    log_message("Deteniendo modo automático...")
    update_ui_status()
    
    # Mostrar notificación usando el módulo de compatibilidad si está disponible
    try:
        from src.utils.ttkbootstrap_compat import show_toast
        show_toast("Modo Automático", "Modo automático detenido", "warning")
    except ImportError:
        # Fallback
        if root and root.winfo_exists() and USING_TTKBOOTSTRAP:
            try:
                from ttkbootstrap.toast import ToastNotification
                ToastNotification(
                    title="Modo Automático",
                    message="Modo automático detenido",
                    duration=3000,
                    bootstyle="warning"
                ).show_toast()
            except Exception as e:
                log_message(f"Error al mostrar notificación: {e}", level='debug')
                try:
                    from tkinter import messagebox
                    messagebox.showinfo("Modo Automático", "Modo automático detenido")
                except:
                    pass

def auto_mode_loop(config):
    """Bucle principal del modo automático"""
    global auto_running, running
    
    log_message("Iniciando bucle automático")
    
    while auto_running and running:
        try:
            tables = find_poker_tables()
            if tables:
                for hwnd, title in tables:
                    if not auto_running or not running:
                        break
                    
                    log_message(f"Procesando mesa: {title}")
                    analyze_table(hwnd, config)
                    time.sleep(1)  # Pausa entre mesas
            
            # Esperar antes de siguiente ciclo
            for _ in range(config["auto_check_interval"]):
                if not auto_running or not running:
                    break
                time.sleep(1)
        except Exception as e:
            log_message(f"Error en bucle automático: {e}", level='error')
            time.sleep(5)
    
    log_message("Bucle automático finalizado")

def update_ui_status():
    """Actualiza el estado en la UI"""
    if not root or not root.winfo_exists():
        return
    
    try:
        for tab in tab_control.winfo_children():
            if hasattr(tab, 'winfo_name') and tab.winfo_name() == "main_tab":
                # Buscar el status_frame recursivamente
                def find_status_frame(widget):
                    if hasattr(widget, 'winfo_name') and widget.winfo_name() == "status_frame":
                        return widget
                    elif hasattr(widget, 'winfo_children'):
                        for child in widget.winfo_children():
                            result = find_status_frame(child)
                            if result:
                                return result
                    return None
                
                status_frame = find_status_frame(tab)
                
                if status_frame:
                    # Buscar label de estado y botón de modo automático
                    for container in status_frame.winfo_children():
                        if isinstance(container, ttk.Frame):
                            for widget in container.winfo_children():
                                # Actualizar etiqueta de estado
                                if isinstance(widget, ttk.Label) and widget not in [None, container.winfo_children()[0]]:
                                    if USING_TTKBOOTSTRAP:
                                        try:
                                            widget.config(
                                                text="Activo",
                                                bootstyle="success" if auto_running else "danger"
                                            )
                                        except:
                                            widget.config(text="Activo" if auto_running else "Inactivo")
                                    else:
                                        widget.config(
                                            text="Activo" if auto_running else "Inactivo",
                                            foreground="green" if auto_running else "red"
                                        )
                                
                                # Actualizar botón de modo automático
                                if isinstance(widget, ttk.Button):
                                    if auto_running:
                                        if USING_TTKBOOTSTRAP:
                                            try:
                                                widget.config(
                                                    text="🛑 Detener",
                                                    bootstyle="danger",
                                                    command=stop_auto_mode
                                                )
                                            except:
                                                widget.config(
                                                    text="Detener modo automático",
                                                    command=stop_auto_mode
                                                )
                                        else:
                                            widget.config(
                                                text="Detener modo automático",
                                                command=stop_auto_mode
                                            )
                                    else:
                                        if USING_TTKBOOTSTRAP:
                                            try:
                                                widget.config(
                                                    text="▶️ Iniciar",
                                                    bootstyle="success",
                                                    command=lambda: start_auto_mode(get_current_config())
                                                )
                                            except:
                                                widget.config(
                                                    text="Iniciar modo automático",
                                                    command=lambda: start_auto_mode(get_current_config())
                                                )
                                        else:
                                            widget.config(
                                                text="Iniciar modo automático",
                                                command=lambda: start_auto_mode(get_current_config())
                                            )
    except Exception as e:
        log_message(f"Error al actualizar UI: {e}", level='error')

def update_history_ui():
    """Actualiza la interfaz del historial"""
    global history_treeview
    
    if not history_treeview or not root or not root.winfo_exists():
        log_message("No se pudo acceder al widget de historial", level='warning')
        return
    
    try:
        from src.ui.tabs.history_tab import update_history_treeview
        update_history_treeview(history_treeview)
        log_message("Historial UI actualizado correctamente")
    except Exception as e:
        log_message(f"Error al actualizar UI del historial: {e}", level='warning')
        import traceback
        log_message(traceback.format_exc(), level='debug')

def get_current_config():
    """Obtiene la configuración actual desde las pestañas de UI"""
    from src.config.settings import load_config
    # Recargar configuración del archivo para obtener cambios recientes
    return load_config()

def on_closing():
    """Maneja el cierre de la aplicación"""
    global running, auto_running
    
    # Usar el módulo de compatibilidad si está disponible
    try:
        from src.utils.ttkbootstrap_compat import show_message
        message_result = show_message("Salir", "¿Estás seguro de querer salir?", "question")
    except ImportError:
        # Fallback al método estándar
        try:
            # Asegurarse de importar messagebox
            from tkinter import messagebox
            
            try:
                if USING_TTKBOOTSTRAP:
                    try:
                        from ttkbootstrap.dialogs import Messagebox
                        message_result = Messagebox.yesno("Salir", "¿Estás seguro de querer salir?")
                    except:
                        message_result = messagebox.askyesno("Salir", "¿Estás seguro de querer salir?")
                else:
                    message_result = messagebox.askyesno("Salir", "¿Estás seguro de querer salir?")
            except:
                # Fallback
                message_result = messagebox.askyesno("Salir", "¿Estás seguro de querer salir?")
        except Exception as e:
            log_message(f"Error en diálogo de cierre: {e}", level='warning')
            # Si no podemos mostrar el diálogo, asumimos que el usuario quiere salir
            message_result = True
    
    if message_result:
        # Detener procesos en segundo plano
        running = False
        auto_running = False
        
        # Guardar configuración final
        try:
            config = get_current_config()
            from src.config.settings import save_config
            save_config(config)
        except Exception as e:
            log_message(f"Error al guardar configuración final: {e}", level='warning')
            
        # Cerrar logs
        log_message("Aplicación cerrada correctamente")
        
        # Destruir ventana
        root.destroy()