import tkinter as tk
from tkinter import messagebox

# Importación segura de ttkbootstrap
try:
    from src.utils.ttkbootstrap_compat import (
        ttk, USING_TTKBOOTSTRAP, FALLBACK_MODE, show_message, 
        create_themed_button, create_themed_label, show_toast, 
        apply_theme_to_toplevel, COLORS
    )
    USING_COMPAT = True
except ImportError:
    # Fallback a importaciones estándar
    USING_COMPAT = False
    try:
        import ttkbootstrap as ttk
        from ttkbootstrap.constants import *
        
        # Intentar importar ToastNotification de manera segura
        try:
            from ttkbootstrap.toast import ToastNotification
            HAS_TOAST = True
        except ImportError:
            # Si no se encuentra el módulo toast, crear un fallback
            HAS_TOAST = False
            
        try:
            from ttkbootstrap.dialogs import MessageDialog, Messagebox
            HAS_TTK_MESSAGEBOX = True
        except ImportError:
            # Si no está disponible en dialogs, intentar otras ubicaciones conocidas
            try:
                from ttkbootstrap.windows import MessageDialog, Messagebox
                HAS_TTK_MESSAGEBOX = True
            except ImportError:
                # Como último recurso, usar el messagebox estándar de tkinter
                HAS_TTK_MESSAGEBOX = False
                
        USING_TTKBOOTSTRAP = True
    except ImportError:
        from tkinter import ttk
        HAS_TOAST = False
        HAS_TTK_MESSAGEBOX = False
        USING_TTKBOOTSTRAP = False

from src.utils.logger import log_message

def show_details_dialog(parent, history_entry, config):
    """Muestra un diálogo con los detalles de una entrada del historial"""
    # Crear ventana de diálogo
    dialog = tk.Toplevel(parent)
    dialog.title(f"Detalles de {history_entry.get('nick', 'Jugador')}")
    dialog.geometry("700x500")
    dialog.minsize(600, 400)
    
    # Aplicar tema directamente (tema oscuro forzado)
    tema_config = config.get("tema", "dark")
    is_dark = tema_config == "dark"
    
    # Forzar tema oscuro directamente a la ventana
    if is_dark:
        try:
            # Configurar colores directamente para asegurar tema oscuro
            dialog.configure(bg="#2d2d30")
            
            # Importar y aplicar tema con el módulo de compatibilidad
            if USING_COMPAT:
                try:
                    from src.utils.ttkbootstrap_compat import apply_theme_to_toplevel
                    apply_theme_to_toplevel(dialog, "dark")
                except ImportError:
                    pass
            elif USING_TTKBOOTSTRAP:
                try:
                    # Intentar aplicar tema desde ttkbootstrap
                    from ttkbootstrap.style import Style
                    dialog_style = Style(theme="darkly")
                    dialog_style.master = dialog
                except:
                    pass
        except Exception as e:
            log_message(f"Error al aplicar tema oscuro: {e}", level='debug')
    
    # Centrar ventana
    dialog.update_idletasks()
    w = dialog.winfo_width()
    h = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (w // 2)
    y = (dialog.winfo_screenheight() // 2) - (h // 2)
    dialog.geometry(f"{w}x{h}+{x}+{y}")
    
    # Hacer ventana modal
    dialog.transient(parent)
    dialog.grab_set()
    
    # Crear una estructura de pestañas para organizar la información
    try:
        if USING_COMPAT:
            notebook = ttk.Notebook(dialog)
            if is_dark:
                notebook.configure(style="dark.TNotebook")
        elif USING_TTKBOOTSTRAP:
            notebook = ttk.Notebook(dialog, bootstyle="primary")
        else:
            notebook = ttk.Notebook(dialog)
            if is_dark:
                style = ttk.Style()
                style.configure("TNotebook", background="#2d2d30", foreground="white")
                style.configure("TNotebook.Tab", background="#3e3e42", foreground="white")
                style.map("TNotebook.Tab", background=[("selected", "#007acc")], 
                         foreground=[("selected", "white")])
    except Exception as e:
        log_message(f"Error al crear notebook: {e}", level='debug')
        notebook = ttk.Notebook(dialog)
    
    # Pestaña de información general
    info_tab = ttk.Frame(notebook, padding=10)
    if is_dark and not USING_TTKBOOTSTRAP:
        info_tab.configure(style="dark.TFrame")
    notebook.add(info_tab, text="Información")
    
    # Contenido de la pestaña de información
    row = 0
    
    # Canvas con scroll para contenido
    canvas_frame = ttk.Frame(info_tab)
    canvas_frame.grid(row=0, column=0, sticky="nsew")
    info_tab.grid_rowconfigure(0, weight=1)
    info_tab.grid_columnconfigure(0, weight=1)
    
    canvas = tk.Canvas(canvas_frame, bg="#2d2d30" if is_dark else "#f5f5f5", 
                      highlightthickness=0)
    if is_dark:
        canvas.configure(bg="#2d2d30")
    
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    content_frame = ttk.Frame(canvas)
    
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    # Bind para canvas
    def configure_canvas(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig("content", width=event.width)
    
    content_frame.bind("<Configure>", configure_canvas)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig("content", width=e.width))
    
    # Añadir frame a canvas
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw", tags="content")
    
    # Mouse wheel binding
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Función para agregar campos
    def add_field(label_text, value, is_heading=False, multiline=False):
        nonlocal row
        
        if is_heading:
            try:
                if USING_COMPAT:
                    heading = create_themed_label(content_frame, label_text, "primary", font=("", 12, "bold"))
                elif USING_TTKBOOTSTRAP:
                    heading = ttk.Label(content_frame, text=label_text, font=("", 12, "bold"), bootstyle="primary")
                else:
                    heading = ttk.Label(content_frame, text=label_text, font=("", 12, "bold"))
                    if is_dark:
                        heading.configure(foreground="white", background="#2d2d30")
            except Exception:
                heading = ttk.Label(content_frame, text=label_text, font=("", 12, "bold"))
                if is_dark:
                    heading.configure(foreground="white", background="#2d2d30")
                
            heading.grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 5))
        else:
            lbl = ttk.Label(content_frame, text=f"{label_text}:")
            if is_dark and not USING_TTKBOOTSTRAP:
                lbl.configure(foreground="white", background="#2d2d30")
            lbl.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            if multiline:
                # Para texto largo, usar un widget Text con desplazamiento - MEJORADO
                frame = ttk.Frame(content_frame, height=200)
                frame.grid(row=row, column=1, sticky="nswe", padx=5, pady=2)
                frame.grid_propagate(False)  # Impedir que el frame se reduzca
                
                text_widget = tk.Text(frame, wrap="word", height=8, width=40)
                if is_dark:
                    text_widget.configure(foreground="white", background="#2d2d30", 
                                        insertbackground="white")
                text_widget.pack(side="left", fill="both", expand=True)
                
                # Crear scrollbar con estilo adecuado
                if USING_TTKBOOTSTRAP:
                    try:
                        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview, bootstyle="round")
                    except:
                        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
                else:
                    scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
                
                text_widget.config(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y")
                
                # Insertar texto
                text_widget.insert("1.0", value)
                text_widget.config(state="disabled")  # Solo lectura
            else:
                # Para valores simples, usar una etiqueta
                value_label = ttk.Label(content_frame, text=value, wraplength=400, justify="left")
                if is_dark and not USING_TTKBOOTSTRAP:
                    value_label.configure(foreground="white", background="#2d2d30")
                value_label.grid(row=row, column=1, sticky="w", padx=5, pady=2)
        
        row += 1
    
    # Información principal
    add_field("Información del Jugador", "", is_heading=True)
    add_field("Nick", history_entry.get("nick", ""))
    add_field("Sala", history_entry.get("sala", ""))
    add_field("Fecha", history_entry.get("timestamp", ""))
    
    # Stats
    add_field("Estadísticas", "", is_heading=True)
    add_field("Stats", history_entry.get("stats", ""), multiline=True)
    
    # Análisis
    if "analisis" in history_entry and history_entry["analisis"].strip():
        add_field("Análisis", "", is_heading=True)
        add_field("Análisis del Juego", history_entry.get("analisis", ""), multiline=True)
    
    # Notas adicionales
    if "notas" in history_entry and history_entry["notas"].strip():
        add_field("Notas Adicionales", "", is_heading=True)
        add_field("Notas", history_entry.get("notas", ""), multiline=True)
    
    # Pestaña de acciones
    actions_tab = ttk.Frame(notebook, padding=10)
    if is_dark and not USING_TTKBOOTSTRAP:
        actions_tab.configure(style="dark.TFrame")
    notebook.add(actions_tab, text="Acciones")
    
    # Frame para botones
    button_frame = ttk.Frame(actions_tab, padding=10)
    if is_dark and not USING_TTKBOOTSTRAP:
        button_frame.configure(style="dark.TFrame")
    button_frame.pack(fill="x", padx=10, pady=10)
    
    # Botón para copiar stats
    def copy_stats():
        stats = history_entry.get("stats", "").strip()
        if stats:
            try:
                dialog.clipboard_clear()
                dialog.clipboard_append(stats)
                dialog.update()
                if USING_COMPAT:
                    show_toast("PokerPRO TRACK", "Estadísticas copiadas al portapapeles")
                elif USING_TTKBOOTSTRAP and HAS_TOAST:
                    try:
                        ToastNotification(
                            title="PokerPRO TRACK",
                            message="Estadísticas copiadas al portapapeles",
                            duration=2000,
                            bootstyle="success"
                        ).show_toast()
                    except Exception as e:
                        log_message(f"Error al mostrar toast: {e}", level='debug')
                        messagebox.showinfo("PokerPRO TRACK", "Estadísticas copiadas al portapapeles")
                else:
                    messagebox.showinfo("PokerPRO TRACK", "Estadísticas copiadas al portapapeles")
            except Exception as e:
                log_message(f"Error al copiar stats: {e}", level='error')
                if USING_COMPAT:
                    show_message("Error", f"Error al copiar stats: {e}", "error")
                else:
                    messagebox.showerror("Error", f"Error al copiar stats: {e}")
        else:
            if USING_COMPAT:
                show_message("Info", "No hay estadísticas para copiar", "info")
            else:
                messagebox.showinfo("Info", "No hay estadísticas para copiar")
    
    # Botón para copiar análisis
    def copy_analysis():
        analysis = history_entry.get("analisis", "").strip()
        if analysis:
            try:
                dialog.clipboard_clear()
                dialog.clipboard_append(analysis)
                dialog.update()
                if USING_COMPAT:
                    show_toast("PokerPRO TRACK", "Análisis copiado al portapapeles")
                elif USING_TTKBOOTSTRAP and HAS_TOAST:
                    try:
                        ToastNotification(
                            title="PokerPRO TRACK",
                            message="Análisis copiado al portapapeles",
                            duration=2000,
                            bootstyle="success"
                        ).show_toast()
                    except:
                        messagebox.showinfo("PokerPRO TRACK", "Análisis copiado al portapapeles")
                else:
                    messagebox.showinfo("PokerPRO TRACK", "Análisis copiado al portapapeles")
            except Exception as e:
                log_message(f"Error al copiar análisis: {e}", level='error')
                if USING_COMPAT:
                    show_message("Error", f"Error al copiar análisis: {e}", "error")
                else:
                    messagebox.showerror("Error", f"Error al copiar análisis: {e}")
        else:
            if USING_COMPAT:
                show_message("Info", "No hay análisis para copiar", "info")
            else:
                messagebox.showinfo("Info", "No hay análisis para copiar")
    
    # Botón para copiar todo
    def copy_all():
        nick = history_entry.get("nick", "")
        stats = history_entry.get("stats", "")
        analysis = history_entry.get("analisis", "")
        
        text = f"Jugador: {nick}\n\n"
        if stats:
            text += f"Stats:\n{stats}\n\n"
        if analysis:
            text += f"Análisis:\n{analysis}"
        
        try:
            dialog.clipboard_clear()
            dialog.clipboard_append(text)
            dialog.update()
            
            if USING_COMPAT:
                show_toast("PokerBot Pro", "Toda la información copiada al portapapeles")
            elif USING_TTKBOOTSTRAP and HAS_TOAST:
                try:
                    ToastNotification(
                        title="PokerBot Pro",
                        message="Toda la información copiada al portapapeles",
                        duration=2000,
                        bootstyle="success"
                    ).show_toast()
                except:
                    messagebox.showinfo("PokerBot Pro", "Toda la información copiada al portapapeles")
            else:
                messagebox.showinfo("PokerBot Pro", "Toda la información copiada al portapapeles")
        except Exception as e:
            log_message(f"Error al copiar información: {e}", level='error')
            if USING_COMPAT:
                show_message("Error", f"Error al copiar información: {e}", "error")
            else:
                messagebox.showerror("Error", f"Error al copiar información: {e}")
    
    # Agregar botones - usar create_themed_button del módulo de compatibilidad si está disponible
    if USING_COMPAT:
        btn1 = create_themed_button(button_frame, "Copiar Stats", copy_stats, "success")
        btn1.pack(side="left", padx=5, pady=5)
        
        btn2 = create_themed_button(button_frame, "Copiar Análisis", copy_analysis, "info")
        btn2.pack(side="left", padx=5, pady=5)
        
        btn3 = create_themed_button(button_frame, "Copiar Todo", copy_all, "warning")
        btn3.pack(side="left", padx=5, pady=5)
    else:
        try:
            if USING_TTKBOOTSTRAP:
                ttk.Button(button_frame, text="Copiar Stats", bootstyle="success", 
                        command=copy_stats).pack(side="left", padx=5, pady=5)
                
                ttk.Button(button_frame, text="Copiar Análisis", bootstyle="info", 
                        command=copy_analysis).pack(side="left", padx=5, pady=5)
                
                ttk.Button(button_frame, text="Copiar Todo", bootstyle="warning", 
                        command=copy_all).pack(side="left", padx=5, pady=5)
            else:
                ttk.Button(button_frame, text="Copiar Stats", 
                        command=copy_stats).pack(side="left", padx=5, pady=5)
                
                ttk.Button(button_frame, text="Copiar Análisis", 
                        command=copy_analysis).pack(side="left", padx=5, pady=5)
                
                ttk.Button(button_frame, text="Copiar Todo", 
                        command=copy_all).pack(side="left", padx=5, pady=5)
        except Exception:
            ttk.Button(button_frame, text="Copiar Stats", 
                    command=copy_stats).pack(side="left", padx=5, pady=5)
            
            ttk.Button(button_frame, text="Copiar Análisis", 
                    command=copy_analysis).pack(side="left", padx=5, pady=5)
            
            ttk.Button(button_frame, text="Copiar Todo", 
                    command=copy_all).pack(side="left", padx=5, pady=5)
    
    # Notas - MEJORADO
    notes_frame = ttk.LabelFrame(actions_tab, text="Notas", padding=10)
    if is_dark and not USING_TTKBOOTSTRAP:
        notes_frame.configure(foreground="white", background="#2d2d30")
    notes_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Contenedor para notas con altura fija
    notes_container = ttk.Frame(notes_frame, height=150)
    if is_dark and not USING_TTKBOOTSTRAP:
        notes_container.configure(style="dark.TFrame")
    notes_container.pack(fill="both", expand=True)
    notes_container.pack_propagate(False)  # Impedir que se reduzca
    
    # Cuadro de texto para notas
    notes_text = tk.Text(notes_container, wrap="word")
    if is_dark:
        notes_text.configure(foreground="white", background="#2d2d30", 
                           insertbackground="white")
    notes_text.insert("1.0", history_entry.get("notas", ""))
    notes_text.pack(side="left", fill="both", expand=True)
    
    # Scrollbar para notas con estilo adecuado
    if USING_TTKBOOTSTRAP:
        try:
            scrollbar = ttk.Scrollbar(notes_container, orient="vertical", command=notes_text.yview, bootstyle="round")
        except:
            scrollbar = ttk.Scrollbar(notes_container, orient="vertical", command=notes_text.yview)
    else:
        scrollbar = ttk.Scrollbar(notes_container, orient="vertical", command=notes_text.yview)
    
    notes_text.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    
    # Función para guardar notas
    def save_notes():
        notes = notes_text.get("1.0", tk.END).strip()
        
        # Actualizar entrada de historial
        history_entry["notas"] = notes
        
        # Guardar historial actualizado
        from src.core.history_manager import load_history, save_history
        history = load_history()
        
        # Buscar y actualizar entrada en el historial
        updated = False
        for i, entry in enumerate(history):
            if (entry.get("timestamp") == history_entry.get("timestamp") and 
                entry.get("nick") == history_entry.get("nick")):
                history[i] = history_entry
                updated = True
                break
        
        if updated:
            if save_history(history):
                if USING_COMPAT:
                    show_toast("PokerBot Pro", "Notas guardadas correctamente")
                elif USING_TTKBOOTSTRAP and HAS_TOAST:
                    try:
                        ToastNotification(
                            title="PokerBot Pro",
                            message="Notas guardadas correctamente",
                            duration=2000,
                            bootstyle="success"
                        ).show_toast()
                    except:
                        messagebox.showinfo("PokerBot Pro", "Notas guardadas correctamente")
                else:
                    messagebox.showinfo("PokerBot Pro", "Notas guardadas correctamente")
            else:
                if USING_COMPAT:
                    show_message("Error", "No se pudieron guardar las notas", "error")
                else:
                    messagebox.showerror("Error", "No se pudieron guardar las notas")
        else:
            if USING_COMPAT:
                show_message("Info", "No se encontró la entrada en el historial", "info")
            else:
                messagebox.showinfo("Info", "No se encontró la entrada en el historial")
    
    # Botón para guardar notas
    if USING_COMPAT:
        save_btn = create_themed_button(actions_tab, "Guardar Notas", save_notes, "primary")
        save_btn.pack(padx=10, pady=10)
    else:
        try:
            if USING_TTKBOOTSTRAP:
                ttk.Button(actions_tab, text="Guardar Notas", bootstyle="primary", 
                        command=save_notes).pack(padx=10, pady=10)
            else:
                ttk.Button(actions_tab, text="Guardar Notas", 
                        command=save_notes).pack(padx=10, pady=10)
        except Exception:
            ttk.Button(actions_tab, text="Guardar Notas", 
                    command=save_notes).pack(padx=10, pady=10)
    
    # Botón para cerrar
    if USING_COMPAT:
        close_btn = create_themed_button(dialog, "Cerrar", dialog.destroy, "secondary")
        close_btn.pack(pady=10)
    else:
        try:
            if USING_TTKBOOTSTRAP:
                ttk.Button(dialog, text="Cerrar", bootstyle="secondary", 
                        command=dialog.destroy).pack(pady=10)
            else:
                ttk.Button(dialog, text="Cerrar", 
                        command=dialog.destroy).pack(pady=10)
        except Exception:
            ttk.Button(dialog, text="Cerrar", 
                    command=dialog.destroy).pack(pady=10)
    
    # Empaquetar notebook
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Intentar añadir ícono
    try:
        dialog.iconbitmap("assets/icon.ico")
    except:
        pass
    
    # Prevenir el error 'can't invoke "event" command: application has been destroyed'
    def on_close_dialog():
        """Función para manejar el cierre correcto del diálogo"""
        try:
            # Limpiar bindings
            canvas.unbind_all("<MouseWheel>")
            # Intentar limpiar eventos pendientes
            dialog.unbind_all("<ThemeChanged>")
            dialog.destroy()
        except Exception as e:
            log_message(f"Error al cerrar diálogo: {e}", level='debug')
    
    # Reemplazar el comando del botón cerrar con nuestra función personalizada
    dialog.protocol("WM_DELETE_WINDOW", on_close_dialog)
    
    # Mostrar diálogo y esperar a que se cierre antes de continuar
    dialog.wait_visibility()  # Esperar a que el diálogo sea visible
    dialog.focus_set()  # Dar foco al diálogo
    
    # En lugar de wait_window, usar grab_set para asegurar que es modal
    dialog.grab_set()