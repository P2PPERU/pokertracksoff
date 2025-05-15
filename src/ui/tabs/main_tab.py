"""
Actualizaciones para manejar Tableview en main_tab.py - Versión específica para ttkbootstrap 1.13.5
"""

import tkinter as tk
import threading

# Función para habilitar el scroll con la rueda del ratón
def enable_mousewheel_scrolling(canvas):
    """Habilita el scroll con la rueda del ratón en un canvas"""
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    # Vincular evento a canvas y todos sus hijos
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Función para limpiar el binding cuando se destruya el canvas
    def _on_destroy(event):
        try:
            canvas.unbind_all("<MouseWheel>")
        except:
            pass
    
    canvas.bind("<Destroy>", _on_destroy)

# Intentar importar desde el módulo de compatibilidad
try:
    from src.utils.ttkbootstrap_compat import (
        ttk, USING_TTKBOOTSTRAP, create_themed_button, 
        create_themed_label, show_message, create_tableview,
        update_tableview
    )
    USING_COMPAT = True
    print("Usando módulo de compatibilidad en main_tab.py")
except ImportError:
    # Fallback a la importación estándar
    USING_COMPAT = False
    try:
        import ttkbootstrap as ttk
        from ttkbootstrap.constants import *
        try:
            from ttkbootstrap.tableview import Tableview
            from ttkbootstrap.scrolled import ScrolledFrame
        except ImportError:
            Tableview = None
            ScrolledFrame = None
        USING_TTKBOOTSTRAP = True
    except ImportError:
        from tkinter import ttk, messagebox
        Tableview = None
        ScrolledFrame = None
        USING_TTKBOOTSTRAP = False

from src.utils.logger import log_message
from src.utils.windows import get_window_under_cursor, find_poker_tables
from src.core.poker_analyzer import analyze_table, copy_last_stats_to_clipboard, copy_last_analysis_to_clipboard, copy_last_results_to_clipboard

def is_tableview_available():
    """Comprueba si Tableview está disponible sin errores"""
    if USING_COMPAT:
        # El módulo de compatibilidad ya maneja esto
        return True
    
    try:
        from ttkbootstrap.tableview import Tableview
        return True
    except Exception:
        return False

def create_main_tab(parent, config):
    """Crea la pestaña principal de la aplicación"""
    # Crear primero un Frame regular como el contenedor principal (hijo directo del Notebook)
    tab = ttk.Frame(parent)
    tab.name = "main_tab"
    
    # Determinar si es tema oscuro
    is_dark = config.get("tema", "dark") == "dark"
    
    # Luego, opcionalmente añadir un ScrolledFrame dentro si está disponible
    try:
        if USING_COMPAT:
            # En este caso, no usamos ScrolledFrame sino nuestro setup_scrolling personalizado
            from src.ui.main_window import setup_scrolling
            content_frame = setup_scrolling(tab)
        elif USING_TTKBOOTSTRAP and ScrolledFrame:
            scroll_frame = ScrolledFrame(tab)
            scroll_frame.pack(fill="both", expand=True)
            # Usar scroll_frame.scrolled_frame como el contenedor para el contenido
            content_frame = scroll_frame.scrolled_frame
            
            # Asegurarnos de que el scroll con rueda funcione
            if hasattr(scroll_frame, "canvas"):
                enable_mousewheel_scrolling(scroll_frame.canvas)
        else:
            # Si no hay ScrolledFrame, crear un canvas propio con scroll
            canvas_frame = ttk.Frame(tab)
            canvas_frame.pack(fill="both", expand=True)
            
            canvas = tk.Canvas(canvas_frame)
            if is_dark:
                canvas.configure(bg="#2d2d30")
                
            scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
            content_frame = ttk.Frame(canvas)
            
            content_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.bind("<Configure>", 
                       lambda e: canvas.itemconfig("window", width=e.width))
            
            canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw", tags="window")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar canvas y scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Habilitar scroll con rueda
            enable_mousewheel_scrolling(canvas)
    except Exception as e:
        log_message(f"Error al crear ScrolledFrame: {e}", level='debug')
        content_frame = tab
    
    # Sección de búsqueda - Diseño con tarjeta
    try:
        if USING_TTKBOOTSTRAP:
            search_card = ttk.Frame(content_frame, bootstyle="light")
        else:
            search_card = ttk.Frame(content_frame)
            if is_dark:
                # Forzar color oscuro en modo fallback
                search_card.configure(style="TFrame")
    except Exception:
        search_card = ttk.Frame(content_frame)
    search_card.pack(fill="x", padx=20, pady=10)
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Label(search_card, text="Búsqueda Manual", font=("", 14, "bold"), 
                    bootstyle="primary").pack(pady=(10,5), padx=10, fill="x")
        else:
            label = ttk.Label(search_card, text="Búsqueda Manual", font=("", 14, "bold"))
            if is_dark:
                try:
                    # Intentar configurar color
                    label.configure(foreground="#007acc")
                except:
                    pass
            label.pack(pady=(10,5), padx=10, fill="x")
    except Exception:
        ttk.Label(search_card, text="Búsqueda Manual", font=("", 14, "bold")).pack(pady=(10,5), padx=10, fill="x")
    
    search_frame = ttk.Frame(search_card, padding=10)
    search_frame.pack(fill="x", padx=10, pady=5)
    search_frame.name = "search_frame"
    
    # Diseño en grid para búsqueda
    search_label = ttk.Label(search_frame, text="Buscar nick:")
    search_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    
    try:
        if USING_TTKBOOTSTRAP:
            entry_nick = ttk.Entry(search_frame, width=30, bootstyle="default")
        else:
            entry_nick = ttk.Entry(search_frame, width=30)
    except Exception:
        entry_nick = ttk.Entry(search_frame, width=30)
    entry_nick.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    # Selector de sala
    sala_var = tk.StringVar(value=config["sala_default"])
    sala_label = ttk.Label(search_frame, text="Sala:")
    sala_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")
    try:
        combo_sala = ttk.Combobox(search_frame, textvariable=sala_var, values=["XPK", "PS", "GG", "WPN", "888"], width=5)
        combo_sala.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    except Exception as e:
        log_message(f"Error al crear combobox: {e}", level='warning')
        # Fallback a Entry
        entry_sala = ttk.Entry(search_frame, width=5, textvariable=sala_var)
        entry_sala.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    
    # Botón de búsqueda
    def search_manual():
        nick = entry_nick.get().strip()
        if not nick:
            # Usar el módulo de compatibilidad si está disponible
            if USING_COMPAT:
                from src.utils.ttkbootstrap_compat import show_message
                show_message("Campo vacío", "Ingresa un nick para buscar", "warning")
            else:
                if USING_TTKBOOTSTRAP:
                    try:
                        from ttkbootstrap.dialogs import Messagebox
                        Messagebox.show_warning("Campo vacío", "Ingresa un nick para buscar")
                    except:
                        from tkinter import messagebox
                        messagebox.showwarning("Campo vacío", "Ingresa un nick para buscar")
                else:
                    from tkinter import messagebox
                    messagebox.showwarning("Campo vacío", "Ingresa un nick para buscar")
            return
            
        # Actualizar sala predeterminada
        config["sala_default"] = sala_var.get()
        from src.config.settings import save_config
        save_config(config)
        
        # Obtener ventana bajo el cursor
        hwnd, _ = get_window_under_cursor()
        if hwnd:
            threading.Thread(target=analyze_table, args=(hwnd, config, nick, True)).start()
        else:
            # Sin mesa específica, buscar la primera disponible
            tables = find_poker_tables()
            if tables:
                hwnd, _ = tables[0]
                threading.Thread(target=analyze_table, args=(hwnd, config, nick, True)).start()
            else:
                log_message("No se encontró una mesa activa para la búsqueda manual", level="warning")
                if USING_COMPAT:
                    from src.utils.ttkbootstrap_compat import show_message
                    show_message("Sin mesa", "No se encontró una mesa de poker activa", "warning")
                else:
                    if USING_TTKBOOTSTRAP:
                        try:
                            from ttkbootstrap.dialogs import Messagebox
                            Messagebox.show_warning("Sin mesa", "No se encontró una mesa de poker activa")
                        except:
                            from tkinter import messagebox
                            messagebox.showwarning("Sin mesa", "No se encontró una mesa de poker activa")
                    else:
                        from tkinter import messagebox
                        messagebox.showwarning("Sin mesa", "No se encontró una mesa de poker activa")
    
    try:
        if USING_COMPAT:
            from src.utils.ttkbootstrap_compat import create_themed_button
            search_btn = create_themed_button(search_frame, "Buscar", search_manual, "primary")
            search_btn.grid(row=0, column=4, padx=5, pady=5)
        elif USING_TTKBOOTSTRAP:
            ttk.Button(search_frame, text="Buscar", bootstyle="primary", 
                    command=search_manual).grid(row=0, column=4, padx=5, pady=5)
        else:
            ttk.Button(search_frame, text="Buscar", 
                    command=search_manual).grid(row=0, column=4, padx=5, pady=5)
    except Exception:
        ttk.Button(search_frame, text="Buscar", 
                command=search_manual).grid(row=0, column=4, padx=5, pady=5)
    
    # Hacer que el Enter en el campo de búsqueda active la búsqueda
    entry_nick.bind("<Return>", lambda event: search_manual())
    
    # Marco para acciones rápidas - Tarjeta moderna
    try:
        if USING_TTKBOOTSTRAP:
            quick_card = ttk.Frame(content_frame, bootstyle="light")
        else:
            quick_card = ttk.Frame(content_frame)
            if is_dark:
                # Forzar color oscuro en modo fallback
                quick_card.configure(style="TFrame")
    except Exception:
        quick_card = ttk.Frame(content_frame)
    quick_card.pack(fill="x", padx=20, pady=10)
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Label(quick_card, text="Acciones Rápidas", font=("", 14, "bold"), 
                    bootstyle="primary").pack(pady=(10,5), padx=10, fill="x")
        else:
            label = ttk.Label(quick_card, text="Acciones Rápidas", font=("", 14, "bold"))
            if is_dark:
                try:
                    # Intentar configurar color
                    label.configure(foreground="#007acc")
                except:
                    pass
            label.pack(pady=(10,5), padx=10, fill="x")
    except Exception:
        ttk.Label(quick_card, text="Acciones Rápidas", font=("", 14, "bold")).pack(pady=(10,5), padx=10, fill="x")
    
    quick_actions_frame = ttk.Frame(quick_card, padding=10)
    quick_actions_frame.pack(fill="x", padx=10, pady=5)
    quick_actions_frame.name = "quick_actions_frame"
    
    # Mejor distribución de botones
    ttk.Label(quick_actions_frame, text="Última búsqueda:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    
    button_frame1 = ttk.Frame(quick_actions_frame)
    button_frame1.grid(row=0, column=1, padx=5, pady=5)
    
    def copy_and_notify(copy_function, message):
        if copy_function():
            if USING_COMPAT:
                from src.utils.ttkbootstrap_compat import show_toast
                show_toast("PokerBot Pro", message)
            elif USING_TTKBOOTSTRAP:
                try:
                    from ttkbootstrap.toast import ToastNotification
                    ToastNotification(
                        title="PokerBot Pro",
                        message=message,
                        duration=2000,
                        bootstyle="success"
                    ).show_toast()
                except Exception as e:
                    # Fallback
                    from tkinter import messagebox
                    messagebox.showinfo("PokerBot Pro", message)
            else:
                from tkinter import messagebox
                messagebox.showinfo("PokerBot Pro", message)
        else:
            if USING_COMPAT:
                from src.utils.ttkbootstrap_compat import show_toast
                show_toast("PokerBot Pro", "No hay datos disponibles", "warning")
            elif USING_TTKBOOTSTRAP:
                try:
                    from ttkbootstrap.toast import ToastNotification
                    ToastNotification(
                        title="PokerBot Pro",
                        message="No hay datos disponibles",
                        duration=2000,
                        bootstyle="warning"
                    ).show_toast()
                except Exception as e:
                    # Fallback
                    from tkinter import messagebox
                    messagebox.showinfo("PokerBot Pro", "No hay datos disponibles")
            else:
                from tkinter import messagebox
                messagebox.showinfo("PokerBot Pro", "No hay datos disponibles")
    
    try:
        if USING_COMPAT:
            from src.utils.ttkbootstrap_compat import create_themed_button
            btn1 = create_themed_button(button_frame1, "📋 Stats", 
                                      lambda: copy_and_notify(copy_last_stats_to_clipboard, "Estadísticas copiadas"), 
                                      "success")
            btn1.pack(side="left", padx=2)
            
            btn2 = create_themed_button(button_frame1, "📋 Análisis", 
                                      lambda: copy_and_notify(copy_last_analysis_to_clipboard, "Análisis copiado"), 
                                      "info")
            btn2.pack(side="left", padx=2)
            
            btn3 = create_themed_button(button_frame1, "📋 Ambos", 
                                      lambda: copy_and_notify(copy_last_results_to_clipboard, "Estadísticas y análisis copiados"), 
                                      "warning")
            btn3.pack(side="left", padx=2)
        elif USING_TTKBOOTSTRAP:
            ttk.Button(button_frame1, text="📋 Stats", bootstyle="success", width=12,
                    command=lambda: copy_and_notify(copy_last_stats_to_clipboard, "Estadísticas copiadas")).pack(side="left", padx=2)
            
            ttk.Button(button_frame1, text="📋 Análisis", bootstyle="info", width=12,
                    command=lambda: copy_and_notify(copy_last_analysis_to_clipboard, "Análisis copiado")).pack(side="left", padx=2)
            
            ttk.Button(button_frame1, text="📋 Ambos", bootstyle="warning", width=12,
                    command=lambda: copy_and_notify(copy_last_results_to_clipboard, "Estadísticas y análisis copiados")).pack(side="left", padx=2)
        else:
            ttk.Button(button_frame1, text="Copiar Stats", width=12,
                    command=lambda: copy_and_notify(copy_last_stats_to_clipboard, "Estadísticas copiadas")).pack(side="left", padx=2)
            
            ttk.Button(button_frame1, text="Copiar Análisis", width=12,
                    command=lambda: copy_and_notify(copy_last_analysis_to_clipboard, "Análisis copiado")).pack(side="left", padx=2)
            
            ttk.Button(button_frame1, text="Copiar Ambos", width=12,
                    command=lambda: copy_and_notify(copy_last_results_to_clipboard, "Estadísticas y análisis copiados")).pack(side="left", padx=2)
    except Exception as e:
        log_message(f"Error al crear botones de acción: {e}", level='warning')
        ttk.Button(button_frame1, text="Copiar Stats", width=12,
                command=lambda: copy_and_notify(copy_last_stats_to_clipboard, "Estadísticas copiadas")).pack(side="left", padx=2)
        
        ttk.Button(button_frame1, text="Copiar Análisis", width=12,
                command=lambda: copy_and_notify(copy_last_analysis_to_clipboard, "Análisis copiado")).pack(side="left", padx=2)
        
        ttk.Button(button_frame1, text="Copiar Ambos", width=12,
                command=lambda: copy_and_notify(copy_last_results_to_clipboard, "Estadísticas y análisis copiados")).pack(side="left", padx=2)
    
    ttk.Label(quick_actions_frame, text="Configuración:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    
    def open_stats_selector():
        try:
            from src.ui.dialogs.stats_selector_dialog import show_stats_selector_dialog
            show_stats_selector_dialog(parent, config)
        except Exception as e:
            log_message(f"Error al abrir selector de estadísticas: {e}", level='error')
            if USING_COMPAT:
                from src.utils.ttkbootstrap_compat import show_message
                show_message("Error", f"No se pudo abrir el selector de estadísticas: {e}", "error")
            else:
                if USING_TTKBOOTSTRAP:
                    try:
                        from ttkbootstrap.dialogs import Messagebox
                        Messagebox.show_error("Error", f"No se pudo abrir el selector de estadísticas: {e}")
                    except:
                        from tkinter import messagebox
                        messagebox.showerror("Error", f"No se pudo abrir el selector de estadísticas: {e}")
                else:
                    from tkinter import messagebox
                    messagebox.showerror("Error", f"No se pudo abrir el selector de estadísticas: {e}")
    
    try:
        if USING_COMPAT:
            from src.utils.ttkbootstrap_compat import create_themed_button
            btn_stats = create_themed_button(quick_actions_frame, "⚙️ Seleccionar Stats", open_stats_selector, "secondary", width=16)
            btn_stats.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        elif USING_TTKBOOTSTRAP:
            ttk.Button(quick_actions_frame, text="⚙️ Seleccionar Stats", bootstyle="secondary", width=16,
                    command=open_stats_selector).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        else:
            ttk.Button(quick_actions_frame, text="Seleccionar Stats", width=16,
                    command=open_stats_selector).grid(row=1, column=1, padx=5, pady=5, sticky="w")
    except Exception:
        ttk.Button(quick_actions_frame, text="Seleccionar Stats", width=16,
                command=open_stats_selector).grid(row=1, column=1, padx=5, pady=5, sticky="w")
    
    # Marco para opciones de salida - Estilo tarjeta
    try:
        if USING_TTKBOOTSTRAP:
            output_card = ttk.Frame(content_frame, bootstyle="light")
        else:
            output_card = ttk.Frame(content_frame)
            if is_dark:
                # Forzar color oscuro en modo fallback
                output_card.configure(style="TFrame")
    except Exception:
        output_card = ttk.Frame(content_frame)
    output_card.pack(fill="x", padx=20, pady=10)
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Label(output_card, text="Opciones de Visualización", font=("", 14, "bold"), 
                    bootstyle="primary").pack(pady=(10,5), padx=10, fill="x")
        else:
            label = ttk.Label(output_card, text="Opciones de Visualización", font=("", 14, "bold"))
            if is_dark:
                try:
                    # Intentar configurar color
                    label.configure(foreground="#007acc")
                except:
                    pass
            label.pack(pady=(10,5), padx=10, fill="x")
    except Exception:
        ttk.Label(output_card, text="Opciones de Visualización", font=("", 14, "bold")).pack(pady=(10,5), padx=10, fill="x")
    
    output_frame = ttk.Frame(output_card, padding=10)
    output_frame.pack(fill="x", padx=10, pady=5)
    output_frame.name = "options_frame"
    
    # Opciones de visualización
    ttk.Label(output_frame, text="Incluir en la salida:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    
    mostrar_stats_var = tk.BooleanVar(value=config["mostrar_stats"])
    mostrar_analisis_var = tk.BooleanVar(value=config["mostrar_analisis"])
    
    def toggle_stats():
        config["mostrar_stats"] = mostrar_stats_var.get()
        from src.config.settings import save_config
        save_config(config)
    
    def toggle_analisis():
        config["mostrar_analisis"] = mostrar_analisis_var.get()
        from src.config.settings import save_config
        save_config(config)
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Checkbutton(output_frame, text="Estadísticas", variable=mostrar_stats_var, 
                        command=toggle_stats, bootstyle="round-toggle").grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            ttk.Checkbutton(output_frame, text="Análisis", variable=mostrar_analisis_var, 
                        command=toggle_analisis, bootstyle="round-toggle").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        else:
            ttk.Checkbutton(output_frame, text="Estadísticas", variable=mostrar_stats_var, 
                        command=toggle_stats).grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            ttk.Checkbutton(output_frame, text="Análisis", variable=mostrar_analisis_var, 
                        command=toggle_analisis).grid(row=0, column=2, padx=5, pady=5, sticky="w")
    except Exception:
        ttk.Checkbutton(output_frame, text="Estadísticas", variable=mostrar_stats_var, 
                     command=toggle_stats).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Checkbutton(output_frame, text="Análisis", variable=mostrar_analisis_var, 
                     command=toggle_analisis).grid(row=0, column=2, padx=5, pady=5, sticky="w")
    
    # Opción de mostrar diálogo de copia
    mostrar_dialogo_var = tk.BooleanVar(value=config.get("mostrar_dialogo_copia", False))
    
    def toggle_dialogo():
        config["mostrar_dialogo_copia"] = mostrar_dialogo_var.get()
        from src.config.settings import save_config
        save_config(config)
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Checkbutton(output_frame, text="Mostrar diálogo de copia", variable=mostrar_dialogo_var, 
                        command=toggle_dialogo, bootstyle="round-toggle").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        else:
            ttk.Checkbutton(output_frame, text="Mostrar diálogo de copia", variable=mostrar_dialogo_var, 
                        command=toggle_dialogo).grid(row=0, column=3, padx=5, pady=5, sticky="w")
    except Exception:
        ttk.Checkbutton(output_frame, text="Mostrar diálogo de copia", variable=mostrar_dialogo_var, 
                     command=toggle_dialogo).grid(row=0, column=3, padx=5, pady=5, sticky="w")
    
    # Marco para estado del modo automático
    try:
        if USING_TTKBOOTSTRAP:
            status_card = ttk.Frame(content_frame, bootstyle="light")
        else:
            status_card = ttk.Frame(content_frame)
            if is_dark:
                # Forzar color oscuro en modo fallback
                status_card.configure(style="TFrame")
    except Exception:
        status_card = ttk.Frame(content_frame)
    status_card.pack(fill="x", padx=20, pady=10)
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Label(status_card, text="Estado del Sistema", font=("", 14, "bold"), 
                    bootstyle="primary").pack(pady=(10,5), padx=10, fill="x")
        else:
            label = ttk.Label(status_card, text="Estado del Sistema", font=("", 14, "bold"))
            if is_dark:
                try:
                    # Intentar configurar color
                    label.configure(foreground="#007acc")
                except:
                    pass
            label.pack(pady=(10,5), padx=10, fill="x")
    except Exception:
        ttk.Label(status_card, text="Estado del Sistema", font=("", 14, "bold")).pack(pady=(10,5), padx=10, fill="x")
    
    status_frame = ttk.Frame(status_card, padding=10)
    status_frame.pack(fill="x", padx=10, pady=5)
    status_frame.name = "status_frame"
    
    from src.ui.main_window import auto_running, start_auto_mode, stop_auto_mode
    
    status_container = ttk.Frame(status_frame)
    status_container.pack(fill="x", padx=5, pady=5)
    
    ttk.Label(status_container, text="Estado del modo automático:", font=("", 10)).pack(side="left", padx=5)
    
    try:
        if USING_TTKBOOTSTRAP:
            estado_label = ttk.Label(status_container, text="Inactivo", bootstyle="danger")
        else:
            estado_label = ttk.Label(status_container, text="Inactivo", foreground="red")
    except Exception:
        estado_label = ttk.Label(status_container, text="Inactivo", foreground="red")
    estado_label.pack(side="left", padx=5)
    
    # Botón para modo automático
    try:
        if USING_COMPAT:
            from src.utils.ttkbootstrap_compat import create_themed_button
            if auto_running:
                btn_auto = create_themed_button(status_container, "🛑 Detener", stop_auto_mode, "danger")
            else:
                btn_auto = create_themed_button(status_container, "▶️ Iniciar", 
                                              lambda: start_auto_mode(config), "success")
            btn_auto.pack(side="right", padx=5)
        elif USING_TTKBOOTSTRAP:
            if auto_running:
                btn_auto = ttk.Button(status_container, text="🛑 Detener", 
                                    bootstyle="danger", command=stop_auto_mode)
            else:
                btn_auto = ttk.Button(status_container, text="▶️ Iniciar", 
                                    bootstyle="success", command=lambda: start_auto_mode(config))
            btn_auto.pack(side="right", padx=5)
        else:
            if auto_running:
                btn_auto = ttk.Button(status_container, text="Detener modo automático", 
                                    command=stop_auto_mode)
            else:
                btn_auto = ttk.Button(status_container, text="Iniciar modo automático", 
                                    command=lambda: start_auto_mode(config))
            btn_auto.pack(side="right", padx=5)
    except Exception as e:
        log_message(f"Error al crear botón de modo automático: {e}", level='warning')
        if auto_running:
            btn_auto = ttk.Button(status_container, text="Detener modo automático", 
                                command=stop_auto_mode)
        else:
            btn_auto = ttk.Button(status_container, text="Iniciar modo automático", 
                                command=lambda: start_auto_mode(config))
        btn_auto.pack(side="right", padx=5)
    
    # Marco para mesas detectadas
    try:
        if USING_TTKBOOTSTRAP:
            tables_card = ttk.Frame(content_frame, bootstyle="light")
        else:
            tables_card = ttk.Frame(content_frame)
            if is_dark:
                # Forzar color oscuro en modo fallback
                tables_card.configure(style="TFrame")
    except Exception:
        tables_card = ttk.Frame(content_frame)
    tables_card.pack(fill="x", padx=20, pady=10, expand=True)
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Label(tables_card, text="Mesas Detectadas", font=("", 14, "bold"), 
                    bootstyle="primary").pack(pady=(10,5), padx=10, fill="x")
        else:
            label = ttk.Label(tables_card, text="Mesas Detectadas", font=("", 14, "bold"))
            if is_dark:
                try:
                    # Intentar configurar color
                    label.configure(foreground="#007acc")
                except:
                    pass
            label.pack(pady=(10,5), padx=10, fill="x")
    except Exception:
        ttk.Label(tables_card, text="Mesas Detectadas", font=("", 14, "bold")).pack(pady=(10,5), padx=10, fill="x")
    
    tables_frame = ttk.Frame(tables_card, padding=10)
    tables_frame.pack(fill="both", expand=True, padx=10, pady=5)
    tables_frame.name = "tables_frame"
    
    # Lista de mesas con un diseño mejorado
    columns = [
        {"text": "ID", "stretch": False, "width": 80},
        {"text": "Título", "stretch": True, "width": 400}
    ]
    
    # Usar el módulo de compatibilidad si está disponible para crear la tabla
    if USING_COMPAT:
        try:
            from src.utils.ttkbootstrap_compat import create_tableview
            tree = create_tableview(tables_frame, columns, height=8, bootstyle="primary")
            tree.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Buscar el canvas en el tableview para habilitar mousewheel
            for child in tree.winfo_children():
                if isinstance(child, tk.Canvas):
                    enable_mousewheel_scrolling(child)
                    break
        except Exception as e:
            log_message(f"Error al crear tabla con módulo de compatibilidad: {e}", level='error')
            # Fallback a Treeview estándar
            tree = ttk.Treeview(tables_frame, columns=("id", "titulo"), show="headings", height=8)
            tree.heading("id", text="ID")
            tree.heading("titulo", text="Título")
            tree.column("id", width=80)
            tree.column("titulo", width=400)
            # Añadir scrollbar
            scrollbar = ttk.Scrollbar(tables_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            tree.pack(fill="both", expand=True, padx=5, pady=5)
    else:
        # Creación condicional del widget de historial
        try:
            if USING_TTKBOOTSTRAP and Tableview and is_tableview_available():
                try:
                    coldata = [
                        {"text": "ID", "stretch": False, "width": 80},
                        {"text": "Título", "stretch": True, "width": 400}
                    ]
                    tree = Tableview(
                        master=tables_frame,
                        coldata=coldata,
                        rowdata=[],
                        paginated=True,
                        searchable=True,
                        bootstyle="primary",
                        height=8
                    )
                    
                    # Buscar el canvas en el tableview para habilitar mousewheel
                    for child in tree.winfo_children():
                        if isinstance(child, tk.Canvas):
                            enable_mousewheel_scrolling(child)
                            break
                except Exception as e:
                    log_message(f"Error al crear Tableview: {e}", level='debug')
                    # Fallback a Treeview estándar
                    tree = ttk.Treeview(tables_frame, columns=("id", "titulo"), show="headings", height=8)
                    tree.heading("id", text="ID")
                    tree.heading("titulo", text="Título")
                    tree.column("id", width=80)
                    tree.column("titulo", width=400)
                    # Añadir scrollbar
                    scrollbar = ttk.Scrollbar(tables_frame, orient="vertical", command=tree.yview)
                    tree.configure(yscrollcommand=scrollbar.set)
                    scrollbar.pack(side="right", fill="y")
            else:
                # Crear un Treeview estándar como alternativa
                tree = ttk.Treeview(tables_frame, columns=("id", "titulo"), show="headings", height=8)
                tree.heading("id", text="ID")
                tree.heading("titulo", text="Título")
                tree.column("id", width=80)
                tree.column("titulo", width=400)
                # Añadir scrollbar
                scrollbar = ttk.Scrollbar(tables_frame, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y")
        except Exception as e:
            log_message(f"Error al crear cualquier tipo de tabla: {e}", level='error')
            # Última opción: un listbox simple
            tree = tk.Listbox(tables_frame, height=8)
            scrollbar = ttk.Scrollbar(tables_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
    
        tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    # Frame para botones
    button_frame = ttk.Frame(tables_frame)
    button_frame.pack(fill="x", padx=5, pady=5)
    
    # Botón para refrescar mesas
    def refresh_tables():
        # Buscar mesas
        tables = find_poker_tables()
        
        # Preparar datos para mostrar
        rowdata = []
        if tables:
            for hwnd, title in tables:
                rowdata.append((hwnd, title))
        else:
            log_message("No se encontraron mesas de poker activas", level="warning")
            rowdata.append(("", "No se encontraron mesas de poker activas"))
        
        # Actualizar tabla usando el módulo de compatibilidad si está disponible
        if USING_COMPAT:
            try:
                from src.utils.ttkbootstrap_compat import update_tableview
                update_tableview(tree, rowdata)
            except Exception as e:
                log_message(f"Error al actualizar tabla con módulo de compatibilidad: {e}", level='error')
                # Intentar método directo
                try:
                    # Limpiar tabla
                    if hasattr(tree, 'delete_rows'):
                        tree.delete_rows()
                    elif hasattr(tree, 'get_children'):
                        for item in tree.get_children():
                            tree.delete(item)
                    elif hasattr(tree, 'delete'):
                        tree.delete(0, tk.END)
                        
                    # Añadir nuevos datos
                    if hasattr(tree, 'build_table_data'):
                        coldata = [
                            {"text": "ID", "stretch": False, "width": 80},
                            {"text": "Título", "stretch": True, "width": 400}
                        ]
                        tree.build_table_data(coldata=coldata, rowdata=rowdata)
                    elif hasattr(tree, 'insert') and hasattr(tree, 'heading'):
                        for row in rowdata:
                            tree.insert("", "end", values=row)
                    elif hasattr(tree, 'insert'):
                        for row in rowdata:
                            tree.insert(tk.END, f"{row[0]}: {row[1]}")
                except Exception as e2:
                    log_message(f"Error en fallback para actualizar tabla: {e2}", level='error')
        else:
            try:
                # Limpiar treeview
                if hasattr(tree, 'delete_rows'):
                    tree.delete_rows()
                    
                    # Para Tableview
                    if hasattr(tree, 'build_table_data'):
                        coldata = [
                            {"text": "ID", "stretch": False, "width": 80},
                            {"text": "Título", "stretch": True, "width": 400}
                        ]
                        tree.build_table_data(coldata=coldata, rowdata=rowdata)
                elif hasattr(tree, 'get_children'):
                    # Para Treeview estándar
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    # Añadir nuevos datos
                    for row in rowdata:
                        tree.insert("", "end", values=row)
                else:
                    # Para Listbox u otro widget
                    tree.delete(0, tk.END)
                    
                    # Añadir nuevos datos
                    for row in rowdata:
                        tree.insert(tk.END, f"{row[0]}: {row[1]}")
            except Exception as e:
                log_message(f"Error al actualizar lista de mesas: {e}", level='error')
    
    # Crear botón con el módulo de compatibilidad si está disponible
    if USING_COMPAT:
        from src.utils.ttkbootstrap_compat import create_themed_button
        refresh_btn = create_themed_button(button_frame, "🔄 Refrescar Mesas", refresh_tables, "info")
        refresh_btn.pack(side="left", padx=5, pady=5)
    else:
        try:
            if USING_TTKBOOTSTRAP:
                ttk.Button(button_frame, text="🔄 Refrescar Mesas", bootstyle="info", 
                        command=refresh_tables).pack(side="left", padx=5, pady=5)
            else:
                ttk.Button(button_frame, text="Refrescar Mesas", 
                        command=refresh_tables).pack(side="left", padx=5, pady=5)
        except Exception:
            ttk.Button(button_frame, text="Refrescar Mesas", 
                    command=refresh_tables).pack(side="left", padx=5, pady=5)
    
    # Botón para analizar mesa seleccionada
    def analyze_selected_table():
        try:
            # Verificamos el tipo de widget de tabla
            table_data = None
            
            if USING_COMPAT:
                # El módulo de compatibilidad debería marcar los widgets como _is_tableview
                if hasattr(tree, '_is_tableview') and tree._is_tableview:
                    # Es un Tableview
                    try:
                        selected = tree.get_rows(selected=True)
                        if not selected:
                            from src.utils.ttkbootstrap_compat import show_message
                            show_message("Sin selección", "Selecciona una mesa para analizar", "warning")
                            return
                        
                        table_data = selected[0]
                    except Exception as e:
                        log_message(f"Error al obtener selección de Tableview: {e}", level='error')
                else:
                    # Es un Treeview estándar
                    try:
                        selection = tree.selection()
                        if not selection:
                            from src.utils.ttkbootstrap_compat import show_message
                            show_message("Sin selección", "Selecciona una mesa para analizar", "warning")
                            return
                        
                        table_data = tree.item(selection[0], "values")
                    except Exception as e:
                        log_message(f"Error al obtener selección de Treeview: {e}", level='error')
            elif hasattr(tree, 'get_rows') and callable(getattr(tree, 'get_rows')):
                # Tableview estándar
                selected = tree.get_rows(selected=True)
                if not selected:
                    if USING_TTKBOOTSTRAP:
                        try:
                            from ttkbootstrap.dialogs import Messagebox
                            Messagebox.show_warning("Sin selección", "Selecciona una mesa para analizar")
                        except:
                            from tkinter import messagebox
                            messagebox.showwarning("Sin selección", "Selecciona una mesa para analizar")
                    else:
                        from tkinter import messagebox
                        messagebox.showwarning("Sin selección", "Selecciona una mesa para analizar")
                    return
                
                table_data = selected[0]
            elif hasattr(tree, 'selection') and callable(getattr(tree, 'selection')):
                # Treeview estándar
                selection = tree.selection()
                if not selection:
                    from tkinter import messagebox
                    messagebox.showwarning("Sin selección", "Selecciona una mesa para analizar")
                    return
                
                table_data = tree.item(selection[0], "values")
            else:
                # Listbox u otro widget
                selected = tree.curselection()
                if not selected:
                    from tkinter import messagebox
                    messagebox.showwarning("Sin selección", "Selecciona una mesa para analizar")
                    return
                
                text = tree.get(selected[0])
                if ":" not in text:
                    from tkinter import messagebox
                    messagebox.showwarning("Selección inválida", "Selecciona una mesa válida para analizar")
                    return
                
                hwnd_str = text.split(":")[0].strip()
                if not hwnd_str:
                    from tkinter import messagebox
                    messagebox.showwarning("Selección inválida", "Selecciona una mesa válida para analizar")
                    return
                    
                table_data = [hwnd_str]
            
            # Verificar si tenemos datos válidos
            if not table_data or not table_data[0]:
                if USING_COMPAT:
                    from src.utils.ttkbootstrap_compat import show_message
                    show_message("Selección inválida", "Selecciona una mesa válida para analizar", "warning")
                else:
                    from tkinter import messagebox
                    messagebox.showwarning("Selección inválida", "Selecciona una mesa válida para analizar")
                return
                
            hwnd = int(table_data[0])
            threading.Thread(target=analyze_table, args=(hwnd, config)).start()
        except Exception as e:
            log_message(f"Error al analizar mesa seleccionada: {e}", level='error')
            if USING_COMPAT:
                from src.utils.ttkbootstrap_compat import show_message
                show_message("Error", f"Error al analizar mesa: {e}", "error")
            else:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Error al analizar mesa: {e}")
    
    # Crear botón con el módulo de compatibilidad si está disponible
    if USING_COMPAT:
        from src.utils.ttkbootstrap_compat import create_themed_button
        analyze_btn = create_themed_button(button_frame, "🔍 Analizar Mesa Seleccionada", analyze_selected_table, "success")
        analyze_btn.pack(side="left", padx=5, pady=5)
    else:
        try:
            if USING_TTKBOOTSTRAP:
                ttk.Button(button_frame, text="🔍 Analizar Mesa Seleccionada", bootstyle="success", 
                        command=analyze_selected_table).pack(side="left", padx=5, pady=5)
            else:
                ttk.Button(button_frame, text="Analizar Mesa Seleccionada", 
                        command=analyze_selected_table).pack(side="left", padx=5, pady=5)
        except Exception:
            ttk.Button(button_frame, text="Analizar Mesa Seleccionada", 
                    command=analyze_selected_table).pack(side="left", padx=5, pady=5)
    
    # Botón para analizar mesa bajo cursor
    def analyze_table_under_cursor():
        hwnd, _ = get_window_under_cursor()
        if hwnd:
            threading.Thread(target=analyze_table, args=(hwnd, config)).start()
        else:
            if USING_COMPAT:
                from src.utils.ttkbootstrap_compat import show_message
                show_message("Sin ventana", "No se encontró una mesa bajo el cursor", "warning")
            elif USING_TTKBOOTSTRAP:
                try:
                    from ttkbootstrap.dialogs import Messagebox
                    Messagebox.show_warning("Sin ventana", "No se encontró una mesa bajo el cursor")
                except:
                    from tkinter import messagebox
                    messagebox.showwarning("Sin ventana", "No se encontró una mesa bajo el cursor")
            else:
                from tkinter import messagebox
                messagebox.showwarning("Sin ventana", "No se encontró una mesa bajo el cursor")
    
    # Crear botón con el módulo de compatibilidad si está disponible
    if USING_COMPAT:
        from src.utils.ttkbootstrap_compat import create_themed_button
        cursor_btn = create_themed_button(button_frame, "🖱️ Analizar Mesa Bajo Cursor", analyze_table_under_cursor, "primary")
        cursor_btn.pack(side="left", padx=5, pady=5)
    else:
        try:
            if USING_TTKBOOTSTRAP:
                ttk.Button(button_frame, text="🖱️ Analizar Mesa Bajo Cursor", bootstyle="primary", 
                        command=analyze_table_under_cursor).pack(side="left", padx=5, pady=5)
            else:
                ttk.Button(button_frame, text="Analizar Mesa Bajo Cursor", 
                        command=analyze_table_under_cursor).pack(side="left", padx=5, pady=5)
        except Exception:
            ttk.Button(button_frame, text="Analizar Mesa Bajo Cursor", 
                    command=analyze_table_under_cursor).pack(side="left", padx=5, pady=5)
    
    # Botón para limpiar caché
    def clear_cache():
        from src.core.poker_analyzer import clear_nick_cache
        clear_nick_cache()
        if USING_COMPAT:
            from src.utils.ttkbootstrap_compat import show_message
            show_message("Caché limpiada", "Se ha limpiado la caché de nicks correctamente", "info")
        elif USING_TTKBOOTSTRAP:
            try:
                from ttkbootstrap.dialogs import Messagebox
                Messagebox.show_info("Caché limpiada", "Se ha limpiado la caché de nicks correctamente")
            except:
                from tkinter import messagebox
                messagebox.showinfo("Caché limpiada", "Se ha limpiado la caché de nicks correctamente")
        else:
            from tkinter import messagebox
            messagebox.showinfo("Caché limpiada", "Se ha limpiado la caché de nicks correctamente")
    
    # Crear botón con el módulo de compatibilidad si está disponible
    if USING_COMPAT:
        from src.utils.ttkbootstrap_compat import create_themed_button
        cache_btn = create_themed_button(button_frame, "🧹 Limpiar Caché", clear_cache, "warning")
        cache_btn.pack(side="right", padx=5, pady=5)
    else:
        try:
            if USING_TTKBOOTSTRAP:
                ttk.Button(button_frame, text="🧹 Limpiar Caché", bootstyle="warning", 
                        command=clear_cache).pack(side="right", padx=5, pady=5)
            else:
                ttk.Button(button_frame, text="Limpiar Caché", 
                        command=clear_cache).pack(side="right", padx=5, pady=5)
        except Exception:
            ttk.Button(button_frame, text="Limpiar Caché", 
                    command=clear_cache).pack(side="right", padx=5, pady=5)
    
    # Inicializar la lista de mesas
    refresh_tables()
    
    return tab