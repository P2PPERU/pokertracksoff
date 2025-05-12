import tkinter as tk
from tkinter import ttk, messagebox
from src.utils.logger import log_message
from src.core.history_manager import load_history, save_history, clear_history as clear_hist
from src.ui.dialogs.details_dialog import show_details_dialog
import threading

def create_history_tab(parent, config):
    """Crea la pestaña de historial"""
    # Crear frame principal
    tab = ttk.Frame(parent)
    tab.name = "tab_historial"
    
    # Crear treeview para historial
    history_tree = ttk.Treeview(tab, columns=("fecha", "nick", "sala", "stats"), show="headings")
    history_tree.heading("fecha", text="Fecha")
    history_tree.heading("nick", text="Nick")
    history_tree.heading("sala", text="Sala")
    history_tree.heading("stats", text="Stats")
    
    history_tree.column("fecha", width=150)
    history_tree.column("nick", width=150)
    history_tree.column("sala", width=50)
    history_tree.column("stats", width=400)
    
    # Scrollbar para el treeview
    scrollbar = ttk.Scrollbar(tab, orient="vertical", command=history_tree.yview)
    history_tree.configure(yscrollcommand=scrollbar.set)
    
    # Frame para botones
    frame_buttons = ttk.Frame(tab, padding=10)
    frame_buttons.pack(side="bottom", fill="x", padx=10, pady=5)
    
    # Botón para ver detalles
    def view_details():
        selection = history_tree.selection()
        if not selection:
            messagebox.showwarning("Sin selección", "Selecciona una entrada para ver detalles")
            return
        
        item = history_tree.item(selection[0])
        date = item["values"][0]
        nick = item["values"][1]
        
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
            messagebox.showwarning("No encontrado", 
                                  f"No se encontraron detalles para {nick} del {date}")
    
    ttk.Button(frame_buttons, text="Ver Detalles", 
              command=view_details).pack(side="left", padx=5)
    
    # Campo de búsqueda
    ttk.Label(frame_buttons, text="Buscar:").pack(side="left", padx=5)
    search_entry = ttk.Entry(frame_buttons, width=30)
    search_entry.pack(side="left", padx=5)
    
    # Función de búsqueda
    def search_history():
        search_text = search_entry.get().strip().lower()
        update_history_treeview(history_tree, search_text)
    
    # Vincular Enter a búsqueda
    search_entry.bind("<Return>", lambda e: search_history())
    
    # Botón de búsqueda
    ttk.Button(frame_buttons, text="Buscar", 
              command=search_history).pack(side="left", padx=5)
    
    # Botón para limpiar historial
    def clear_history():
        if messagebox.askyesno("Confirmar", "¿Estás seguro de querer borrar todo el historial?"):
            clear_hist()
            update_history_treeview(history_tree)
    
    ttk.Button(frame_buttons, text="Limpiar Historial", 
              command=clear_history).pack(side="right", padx=5)
    
    # Empaquetar elementos
    scrollbar.pack(side="right", fill="y")
    history_tree.pack(side="left", fill="both", expand=True)
    
    # Cargar historial inicial
    update_history_treeview(history_tree)
    
    return tab, history_tree

def update_history_treeview(tree, search_text=None):
    """Actualiza el treeview con los datos del historial"""
    from src.utils.logger import log_message
    
    try:
        # Verificar que el tree existe y es válido
        if not tree or not tree.winfo_exists():
            log_message("No se puede actualizar historial: widget no existe", level='warning')
            return
        
        # Limpiar treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Cargar historial 
        history = load_history()
        
        if not history:
            log_message("No hay entradas en el historial")
            tree.insert("", "end", values=("", "El historial está vacío", "", ""))
            return
        
        log_message(f"Actualizando treeview con {len(history)} entradas de historial")
        
        # Filtrar por búsqueda si es necesario
        filtered_entries = []
        
        if search_text:
            log_message(f"Buscando '{search_text}' en historial")
            for entry in history:
                try:
                    # Extraer campos con manejo de errores
                    nick = entry.get("nick", "").lower()
                    stats = entry.get("stats", "").lower()
                    analysis = entry.get("analisis", "").lower()
                    
                    # Buscar en todos los campos
                    if (search_text in nick or 
                        search_text in stats or 
                        search_text in analysis):
                        filtered_entries.append(entry)
                except Exception as e:
                    log_message(f"Error al procesar entrada en búsqueda: {e}", level='error')
                    continue
        else:
            filtered_entries = history
        
        # Mostrar resultados
        if filtered_entries:
            for entry in reversed(filtered_entries):  # Más recientes primero
                try:
                    # Extraer datos con validación
                    timestamp = entry.get("timestamp", "Sin fecha")
                    nick = entry.get("nick", "Sin nick")
                    sala = entry.get("sala", "---")
                    stats = entry.get("stats", "Sin stats")
                    
                    tree.insert("", "end", values=(timestamp, nick, sala, stats))
                except Exception as e:
                    log_message(f"Error al insertar entrada en historial_tree: {e}", level='error')
                    continue
            
            log_message(f"Se mostraron {len(filtered_entries)} entradas en el historial")
        else:
            if search_text:
                tree.insert("", "end", values=("", "No se encontraron resultados", "", ""))
                log_message("Búsqueda sin resultados")
            else:
                tree.insert("", "end", values=("", "El historial está vacío", "", ""))
                log_message("Historial vacío o inaccesible")
    
    except Exception as e:
        log_message(f"Error al actualizar historial UI: {e}", level='error')
        import traceback
        log_message(traceback.format_exc(), level='error')