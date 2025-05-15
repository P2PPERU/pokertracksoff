import tkinter as tk
from tkinter import messagebox

# Importación correcta
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.tableview import Tableview
    # Intentar importar el módulo de diálogos de ttkbootstrap
    try:
        from ttkbootstrap.dialogs import Messagebox as ttk_Messagebox
        HAS_TTK_MESSAGEBOX = True
    except ImportError:
        HAS_TTK_MESSAGEBOX = False
    USING_TTKBOOTSTRAP = True
except ImportError:
    from tkinter import ttk
    Tableview = None
    HAS_TTK_MESSAGEBOX = False
    USING_TTKBOOTSTRAP = False

from src.utils.logger import log_message
from src.core.history_manager import load_history, save_history
from src.ui.dialogs.details_dialog import show_details_dialog
import threading

def is_tableview_available():
    """Comprueba si Tableview está disponible sin errores"""
    try:
        # Intenta crear un Tableview sin usarlo realmente
        # para comprobar si hay errores
        from ttkbootstrap.tableview import Tableview
        return True
    except Exception:
        return False

def create_history_tab(parent, config):
    """Crea la pestaña de historial"""
    # Crear frame principal
    tab = ttk.Frame(parent)
    tab.name = "tab_historial"
    
    # Frame de búsqueda
    search_frame = ttk.Frame(tab, padding=10)
    search_frame.pack(fill="x", side="top")
    
    ttk.Label(search_frame, text="Buscar jugador:", font=("", 10)).pack(side="left", padx=5)
    try:
        if USING_TTKBOOTSTRAP:
            search_entry = ttk.Entry(search_frame, width=30, bootstyle="default")
        else:
            search_entry = ttk.Entry(search_frame, width=30)
    except Exception:
        search_entry = ttk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=5)
    
    # Función de búsqueda
    def search_history():
        search_text = search_entry.get().strip().lower()
        update_history_treeview(history_tree, search_text)
    
    # Vincular Enter a búsqueda
    search_entry.bind("<Return>", lambda e: search_history())
    
    # Botón de búsqueda
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Button(search_frame, text="Buscar", bootstyle="primary", command=search_history).pack(side="left", padx=5)
        else:
            ttk.Button(search_frame, text="Buscar", command=search_history).pack(side="left", padx=5)
    except Exception:
        ttk.Button(search_frame, text="Buscar", command=search_history).pack(side="left", padx=5)
    
    # Crear treeview para historial
    coldata = [
        {"text": "Fecha", "stretch": False, "width": 150},
        {"text": "Nick", "stretch": True, "width": 150},
        {"text": "Sala", "stretch": False, "width": 50},
        {"text": "Stats", "stretch": True, "width": 400},
    ]
    
    # Creación condicional del widget de historial
    try:
        if USING_TTKBOOTSTRAP and Tableview and is_tableview_available():
            try:
                history_tree = Tableview(
                    master=tab,
                    coldata=coldata,
                    rowdata=[],
                    paginated=True,
                    searchable=True,
                    bootstyle="primary",
                    pagesize=15,
                    height=10
                )
                # Almacenar explícitamente los datos de columna para uso posterior
                history_tree.saved_coldata = coldata
                history_tree._is_tableview = True
                history_tree._is_listbox = False
            except Exception as e:
                log_message(f"Error al crear Tableview: {e}", level='debug')
                # Fallback a Treeview estándar
                history_tree = ttk.Treeview(tab, columns=("fecha", "nick", "sala", "stats"), show="headings", height=10)
                history_tree.heading("fecha", text="Fecha")
                history_tree.heading("nick", text="Nick")
                history_tree.heading("sala", text="Sala")
                history_tree.heading("stats", text="Stats")
                
                history_tree.column("fecha", width=150)
                history_tree.column("nick", width=150)
                history_tree.column("sala", width=50)
                history_tree.column("stats", width=400)
                
                # Añadir scrollbar para el treeview
                scrollbar = ttk.Scrollbar(tab, orient="vertical", command=history_tree.yview)
                history_tree.configure(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y")
                history_tree._is_tableview = False
                history_tree._is_listbox = False
        else:
            # Fallback a Treeview estándar
            history_tree = ttk.Treeview(tab, columns=("fecha", "nick", "sala", "stats"), show="headings", height=10)
            history_tree.heading("fecha", text="Fecha")
            history_tree.heading("nick", text="Nick")
            history_tree.heading("sala", text="Sala")
            history_tree.heading("stats", text="Stats")
            
            history_tree.column("fecha", width=150)
            history_tree.column("nick", width=150)
            history_tree.column("sala", width=50)
            history_tree.column("stats", width=400)
            
            # Añadir scrollbar para el treeview
            scrollbar = ttk.Scrollbar(tab, orient="vertical", command=history_tree.yview)
            history_tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            history_tree._is_tableview = False
            history_tree._is_listbox = False
    except Exception as e:
        log_message(f"Error al crear cualquier tipo de tabla: {e}", level='error')
        # Última opción: un listbox simple
        history_tree = tk.Listbox(tab, height=10)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        history_tree._is_tableview = False
        history_tree._is_listbox = True
    
    history_tree.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Frame para botones
    frame_buttons = ttk.Frame(tab, padding=10)
    frame_buttons.pack(side="bottom", fill="x", padx=10, pady=5)
    
    # Botón para ver detalles
    def view_details():
        try:
            # Asegurar que messagebox esté disponible
            from tkinter import messagebox
            
            if hasattr(history_tree, '_is_tableview') and history_tree._is_tableview:
                selected = history_tree.get_rows(selected=True)
                if not selected:
                    if USING_TTKBOOTSTRAP and HAS_TTK_MESSAGEBOX:
                        try:
                            ttk_Messagebox.show_warning("Sin selección", "Selecciona una entrada para ver detalles")
                        except:
                            messagebox.showwarning("Sin selección", "Selecciona una entrada para ver detalles")
                    else:
                        messagebox.showwarning("Sin selección", "Selecciona una entrada para ver detalles")
                    return
                
                # TableRow en ttkbootstrap es un objeto especial que necesita ser accedido de otra manera
                selected_item = selected[0]
                try:
                    # Para TableRow objects
                    if hasattr(selected_item, 'values'):
                        # Acceder a los valores como atributos
                        date = selected_item.values[0]
                        nick = selected_item.values[1]
                    elif hasattr(selected_item, 'text'):
                        # Acceso alternativo
                        values = [cell.text for cell in selected_item.cells]
                        date = values[0]
                        nick = values[1]
                    else:
                        # Si nada funciona, intentar como lista/tupla (forma antigua)
                        date = selected_item[0]
                        nick = selected_item[1]
                except Exception as e:
                    log_message(f"Error al acceder a TableRow: {e}", level='error')
                    log_message(f"Tipo de selected_item: {type(selected_item)}", level='debug')
                    log_message(f"Atributos disponibles: {dir(selected_item)}", level='debug')
                    # Intentar otra forma de obtener la fila seleccionada
                    try:
                        row_id = history_tree.selection()[0]
                        date = history_tree.item(row_id, 'values')[0]
                        nick = history_tree.item(row_id, 'values')[1]
                    except:
                        messagebox.showwarning("Error", "No se pudieron obtener los detalles. Intenta con otra fila.")
                        return
            elif hasattr(history_tree, 'selection') and callable(getattr(history_tree, 'selection')):
                # Para Treeview estándar
                selection = history_tree.selection()
                if not selection:
                    messagebox.showwarning("Sin selección", "Selecciona una entrada para ver detalles")
                    return
                
                item = history_tree.item(selection[0])
                date = item["values"][0]
                nick = item["values"][1]
            else:
                # Para Listbox u otro widget
                selected = history_tree.curselection()
                if not selected:
                    messagebox.showwarning("Sin selección", "Selecciona una entrada para ver detalles")
                    return
                
                # En el caso de Listbox, necesitamos parsear el texto
                text = history_tree.get(selected[0])
                if " - " not in text:
                    messagebox.showwarning("Selección inválida", "Selecciona una entrada válida")
                    return
                
                # Aquí asumimos un formato específico para la salida en Listbox
                parts = text.split(" - ")
                if len(parts) < 2:
                    messagebox.showwarning("Formato inválido", "El formato de la entrada no es válido")
                    return
                
                date = parts[0].strip()
                nick = parts[1].strip()
            
            log_message(f"Buscando detalles para {nick} del {date}")
            
            # Buscar en historial
            history = load_history()
            entry = None
            
            for hist_entry in history:
                if hist_entry.get("timestamp") == date and hist_entry.get("nick") == nick:
                    entry = hist_entry
                    break
            
            if entry:
                show_details_dialog(parent, entry, config)
            else:
                if USING_TTKBOOTSTRAP and HAS_TTK_MESSAGEBOX:
                    try:
                        ttk_Messagebox.show_warning("No encontrado", 
                                      f"No se encontraron detalles para {nick} del {date}")
                    except:
                        messagebox.showwarning("No encontrado", 
                                      f"No se encontraron detalles para {nick} del {date}")
                else:
                    messagebox.showwarning("No encontrado", 
                                      f"No se encontraron detalles para {nick} del {date}")
        except Exception as e:
            log_message(f"Error al mostrar detalles: {e}", level='error')
            import traceback
            log_message(traceback.format_exc(), level='error')
            # Asegurar que messagebox esté importado
            from tkinter import messagebox
            messagebox.showerror("Error", f"Error al mostrar detalles: {e}")
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Button(frame_buttons, text="Ver Detalles", bootstyle="info", 
                    command=view_details).pack(side="left", padx=5)
        else:
            ttk.Button(frame_buttons, text="Ver Detalles", 
                    command=view_details).pack(side="left", padx=5)
    except Exception:
        ttk.Button(frame_buttons, text="Ver Detalles", 
                command=view_details).pack(side="left", padx=5)
    
    # Botón para limpiar historial
    def clear_history():
        try:
            if USING_TTKBOOTSTRAP and HAS_TTK_MESSAGEBOX:
                try:
                    confirm = ttk_Messagebox.yesno("Confirmar", "¿Estás seguro de querer borrar todo el historial?")
                except:
                    confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de querer borrar todo el historial?")
            else:
                confirm = messagebox.askyesno("Confirmar", "¿Estás seguro de querer borrar todo el historial?")
                
            if confirm:
                from src.core.history_manager import clear_history
                clear_history()
                update_history_treeview(history_tree)
        except Exception as e:
            log_message(f"Error al limpiar historial: {e}", level='error')
            messagebox.showerror("Error", f"Error al limpiar historial: {e}")
    
    try:
        if USING_TTKBOOTSTRAP:
            ttk.Button(frame_buttons, text="Limpiar Historial", bootstyle="danger", 
                    command=clear_history).pack(side="right", padx=5)
        else:
            ttk.Button(frame_buttons, text="Limpiar Historial", 
                    command=clear_history).pack(side="right", padx=5)
    except Exception:
        ttk.Button(frame_buttons, text="Limpiar Historial", 
                command=clear_history).pack(side="right", padx=5)
    
    # Cargar historial inicial
    update_history_treeview(history_tree)
    
    return tab, history_tree

def update_history_treeview(tree, search_text=None):
    """Actualiza el treeview con los datos del historial"""
    if not tree:
        log_message("No se pudo acceder al widget de historial", level='warning')
        return
    
    try:
        # Determinar qué tipo de widget es
        is_tableview = hasattr(tree, '_is_tableview') and tree._is_tableview
        is_listbox = hasattr(tree, '_is_listbox') and tree._is_listbox
        
        # Limpiar widget según su tipo
        try:
            if is_tableview:
                # Para Tableview
                if hasattr(tree, 'delete_rows'):
                    tree.delete_rows()
                else:
                    log_message("El Tableview no tiene método delete_rows", level='warning')
            elif is_listbox:
                # Para Listbox
                tree.delete(0, tk.END)
            else:
                # Para Treeview estándar
                for item in tree.get_children():
                    tree.delete(item)
        except Exception as e:
            log_message(f"Error al limpiar widget de historial: {e}", level='warning')
        
        # Cargar historial
        history = load_history()
        
        log_message(f"Actualizando treeview con {len(history)} entradas de historial")
        
        if not history:
            log_message("No hay entradas en el historial")
            return
        
        # Filtrar por búsqueda si es necesario
        filtered_entries = []
        
        if search_text:
            for entry in history:
                nick = entry.get("nick", "").lower()
                stats = entry.get("stats", "").lower()
                analysis = entry.get("analisis", "").lower()
                
                if search_text in nick or search_text in stats or search_text in analysis:
                    filtered_entries.append(entry)
        else:
            filtered_entries = history
        
        if filtered_entries:
            # Preparar datos para mostrar
            rowdata = []
            for entry in reversed(filtered_entries):  # Más recientes primero
                timestamp = entry.get("timestamp", "Sin fecha")
                nick = entry.get("nick", "Sin nick")
                sala = entry.get("sala", "---")
                stats = entry.get("stats", "Sin stats")
                
                rowdata.append((timestamp, nick, sala, stats))
            
            # Actualizar widget según su tipo
            try:
                if is_tableview:
                    # Para Tableview - usar los datos de columna guardados
                    if hasattr(tree, 'saved_coldata'):
                        tree.build_table_data(coldata=tree.saved_coldata, rowdata=rowdata)
                    elif hasattr(tree, 'configure'):
                        # Si no tenemos saved_coldata, intentamos un enfoque alternativo
                        log_message("Usando método alternativo para Tableview", level='debug')
                        default_coldata = [
                            {"text": "Fecha", "stretch": False, "width": 150},
                            {"text": "Nick", "stretch": True, "width": 150},
                            {"text": "Sala", "stretch": False, "width": 50},
                            {"text": "Stats", "stretch": True, "width": 400}
                        ]
                        tree.build_table_data(coldata=default_coldata, rowdata=rowdata)
                    else:
                        log_message("No se pudo encontrar método para actualizar Tableview", level='warning')
                elif is_listbox:
                    # Para Listbox
                    for row in rowdata:
                        tree.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - {row[3]}")
                else:
                    # Para Treeview estándar
                    for row in rowdata:
                        tree.insert("", "end", values=row)
                
                log_message(f"Se mostraron {len(rowdata)} entradas en el historial")
            except Exception as e:
                log_message(f"Error al actualizar datos de historial: {e}", level='error')
                
                # Intento alternativo si falla el método primario
                try:
                    if is_tableview:
                        log_message("Intentando método alternativo para Tableview", level='debug')
                        # Crear un nuevo Tableview como reemplazo
                        parent = tree.master
                        tree.pack_forget()
                        
                        new_tree = ttk.Treeview(parent, columns=("fecha", "nick", "sala", "stats"), show="headings", height=10)
                        new_tree.heading("fecha", text="Fecha")
                        new_tree.heading("nick", text="Nick")
                        new_tree.heading("sala", text="Sala")
                        new_tree.heading("stats", text="Stats")
                        
                        new_tree.column("fecha", width=150)
                        new_tree.column("nick", width=150)
                        new_tree.column("sala", width=50)
                        new_tree.column("stats", width=400)
                        
                        # Añadir datos
                        for row in rowdata:
                            new_tree.insert("", "end", values=row)
                        
                        # Empaquetar el nuevo widget
                        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=new_tree.yview)
                        new_tree.configure(yscrollcommand=scrollbar.set)
                        scrollbar.pack(side="right", fill="y")
                        new_tree.pack(fill="both", expand=True, padx=10, pady=5)
                        
                        # Reemplazar referencia
                        tree._is_tableview = False
                        tree = new_tree
                    elif not is_listbox:
                        # Para Treeview estándar como fallback si no es Tableview ni Listbox
                        for row in rowdata:
                            tree.insert("", "end", values=row)
                except Exception as e2:
                    log_message(f"Error en método alternativo: {e2}", level='error')
        elif search_text:
            # Mostrar mensaje de "no se encontraron resultados"
            try:
                if is_tableview:
                    if hasattr(tree, 'saved_coldata'):
                        tree.build_table_data(coldata=tree.saved_coldata, rowdata=[("", "No se encontraron resultados", "", "")])
                    else:
                        default_coldata = [
                            {"text": "Fecha", "stretch": False, "width": 150},
                            {"text": "Nick", "stretch": True, "width": 150},
                            {"text": "Sala", "stretch": False, "width": 50},
                            {"text": "Stats", "stretch": True, "width": 400}
                        ]
                        tree.build_table_data(coldata=default_coldata, rowdata=[("", "No se encontraron resultados", "", "")])
                elif is_listbox:
                    tree.insert(tk.END, "No se encontraron resultados")
                else:
                    tree.insert("", "end", values=("", "No se encontraron resultados", "", ""))
            except Exception as e:
                log_message(f"Error al mostrar mensaje de no resultados: {e}", level='debug')
    except Exception as e:
        log_message(f"Error general al actualizar historial: {e}", level='error')
        import traceback
        log_message(traceback.format_exc(), level='error')