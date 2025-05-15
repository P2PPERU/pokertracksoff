"""
Módulo de compatibilidad para ttkbootstrap v1.13.5 que evita errores de elementos duplicados.
Proporciona una forma segura de usar funcionalidades básicas de ttkbootstrap.
"""

import tkinter as tk
from tkinter import ttk as tk_ttk
from tkinter import messagebox as tk_messagebox
import sys

# Valores por defecto en caso de no tener ttkbootstrap
USING_TTKBOOTSTRAP = False
FALLBACK_MODE = False

# Colores predefinidos para tema fallback
COLORS = {
    "dark": {
        "bg": "#2d2d30",
        "fg": "#ffffff",
        "primary": "#007acc",
        "secondary": "#3e3e42",
        "success": "#4CAF50",
        "info": "#2196F3",
        "warning": "#FFC107",
        "danger": "#F44336"
    },
    "light": {
        "bg": "#f5f5f5",
        "fg": "#212121",
        "primary": "#007acc",
        "secondary": "#e0e0e0",
        "success": "#4CAF50",
        "info": "#2196F3",
        "warning": "#FFC107",
        "danger": "#F44336"
    }
}

# Inicialización de variables globales
ttk = None
messagebox = tk_messagebox  # Usamos como fallback el messagebox estándar de tkinter
root_window = None
active_theme = "dark"

def disable_conflicting_elements():
    """Deshabilita elementos de ttkbootstrap que causan conflictos"""
    
    # Prevenir que ttkbootstrap modifique scrollbar que causa conflictos
    try:
        import ttkbootstrap
        from ttkbootstrap.style import StylerTTK
        
        # El elemento problemático es create_scrollbar_style
        # Lo reemplazamos con una versión que no haga nada
        original_create_scrollbar = StylerTTK.create_scrollbar_style
        
        def safe_create_scrollbar_style(self, *args, **kwargs):
            try:
                return original_create_scrollbar(self, *args, **kwargs)
            except Exception:
                # Ignorar errores de elementos duplicados
                pass
        
        # Sustituir el método original
        StylerTTK.create_scrollbar_style = safe_create_scrollbar_style
        
        return True
    except Exception:
        return False

def init_ttkbootstrap(theme_name="darkly"):
    """Inicializa ttkbootstrap evitando elementos que causan conflictos"""
    global ttk, messagebox, root_window, USING_TTKBOOTSTRAP, active_theme, FALLBACK_MODE
    
    # Establecer tema predeterminado
    active_theme = "dark" if theme_name in ["darkly", "superhero", "solar", "cyborg"] else "light"
    
    try:
        # Intentar deshabilitar elementos problemáticos
        disable_conflicting_elements()
        
        # Importar ttkbootstrap pero evitando inicialización con Style
        import ttkbootstrap as ttk_bootstrap
        
        # En la versión 1.13.5, messagebox se ha movido a dialogs
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
                
        ttk = ttk_bootstrap
        # Si no pudimos importar MessageDialog, usamos el messagebox estándar de tkinter
        if not HAS_TTK_MESSAGEBOX:
            messagebox = tk_messagebox
        
        USING_TTKBOOTSTRAP = True
        
        print("Modo ttkbootstrap básico inicializado")
        return True
    except Exception as e:
        print(f"Error al inicializar ttkbootstrap: {e}")
        
        # Fallback a ttk estándar
        ttk = tk_ttk
        messagebox = tk_messagebox
        USING_TTKBOOTSTRAP = False
        FALLBACK_MODE = True
        
        # Configurar tema fallback
        style = ttk.Style()
        try:
            style.theme_use("clam")  # Tema base más personalizable
        except:
            pass  # Si no está disponible, usar tema por defecto
        
        # Colores para el tema seleccionado
        colors = COLORS[active_theme]
        
        # Configuración explícita de estilos para modo oscuro
        try:
            # Configurar widgets básicos
            style.configure("TFrame", background=colors["bg"], borderwidth=0)
            style.configure("dark.TFrame", background=colors["bg"], borderwidth=0)
            
            style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
            style.configure("dark.TLabel", background=colors["bg"], foreground=colors["fg"])
            
            style.configure("TButton", background=colors["primary"], foreground="white")
            style.map("TButton", background=[("active", colors["primary"])])
            
            style.configure("TNotebook", background=colors["bg"])
            style.configure("TNotebook.Tab", background=colors["secondary"], foreground=colors["fg"])
            style.map("TNotebook.Tab", background=[("selected", colors["primary"])], 
                     foreground=[("selected", "white")])
            
            style.configure("dark.TNotebook", background=colors["bg"])
            style.configure("dark.TNotebook.Tab", background=colors["secondary"], foreground=colors["fg"])
            style.map("dark.TNotebook.Tab", background=[("selected", colors["primary"])], 
                     foreground=[("selected", "white")])
            
            # Configurar scrollbars para que sean visibles en tema oscuro
            style.configure("Vertical.TScrollbar", background=colors["secondary"], 
                         troughcolor=colors["bg"], bordercolor=colors["secondary"])
            style.map("Vertical.TScrollbar", background=[("active", colors["primary"])])
            
            # LabelFrame para tema oscuro
            style.configure("TLabelframe", background=colors["bg"])
            style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"])
        except Exception as e:
            print(f"Error al configurar estilos fallback: {e}")
        
        print("Fallback a ttk estándar")
        return False

def apply_global_dark_theme():
    """Aplica el tema oscuro a nivel global para todos los widgets"""
    if FALLBACK_MODE or not USING_TTKBOOTSTRAP:
        style = ttk.Style()
        style.theme_use("clam")  # Tema base más adaptable
        
        colors = COLORS["dark"]
        
        # Configuración global para todos los widgets
        style.configure(".", 
                      background=colors["bg"],
                      foreground=colors["fg"],
                      fieldbackground=colors["bg"],
                      troughcolor=colors["secondary"],
                      darkcolor=colors["secondary"],
                      lightcolor=colors["primary"])
        
        # Widgets específicos
        style.configure("TFrame", background=colors["bg"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure("TButton", background=colors["primary"], foreground="white")
        style.map("TButton", background=[("active", colors["primary"])])
        
        style.configure("TNotebook", background=colors["bg"])
        style.configure("TNotebook.Tab", background=colors["secondary"], foreground=colors["fg"])
        style.map("TNotebook.Tab", background=[("selected", colors["primary"])],
                foreground=[("selected", "white")])
        
        style.configure("TScrollbar", background=colors["secondary"], 
                      troughcolor=colors["bg"], arrowcolor=colors["fg"])
        style.map("TScrollbar", background=[("active", colors["primary"])])
        
        style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"])
        style.map("TCheckbutton", background=[("active", colors["bg"])])
        
        style.configure("TRadiobutton", background=colors["bg"], foreground=colors["fg"])
        style.map("TRadiobutton", background=[("active", colors["bg"])])
        
        style.configure("TCombobox", fieldbackground=colors["bg"], 
                      foreground=colors["fg"], background=colors["secondary"])
        style.map("TCombobox", fieldbackground=[("readonly", colors["bg"])])
        
        style.configure("TEntry", fieldbackground=colors["bg"], foreground=colors["fg"])
        
        style.configure("TLabelframe", background=colors["bg"], foreground=colors["fg"])
        style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"])
        
        style.configure("Vertical.TScrollbar", background=colors["secondary"],
                      troughcolor=colors["bg"], arrowcolor=colors["fg"])
        style.map("Vertical.TScrollbar", background=[("active", colors["primary"])])
        
        style.configure("Horizontal.TScrollbar", background=colors["secondary"],
                      troughcolor=colors["bg"], arrowcolor=colors["fg"])
        style.map("Horizontal.TScrollbar", background=[("active", colors["primary"])])
        
        style.configure("Treeview", 
                      background=colors["bg"],
                      foreground=colors["fg"],
                      fieldbackground=colors["bg"])
        style.configure("Treeview.Heading", 
                      background=colors["secondary"],
                      foreground=colors["fg"])
        style.map("Treeview", background=[("selected", colors["primary"])],
                foreground=[("selected", "white")])

def create_themed_button(parent, text, command, style_name="primary", **kwargs):
    """Crea un botón con el estilo especificado"""
    if USING_TTKBOOTSTRAP:
        try:
            # Intentar con bootstyle
            return ttk.Button(parent, text=text, command=command, bootstyle=style_name, **kwargs)
        except:
            # Si falla, intentar con style
            return ttk.Button(parent, text=text, command=command, style=f"{style_name}.TButton", **kwargs)
    else:
        # Modo fallback con colores específicos
        button = ttk.Button(parent, text=text, command=command, **kwargs)
        if active_theme == "dark":
            # Asegurar que los botones sean visibles en tema oscuro
            color = COLORS["dark"][style_name] if style_name in COLORS["dark"] else COLORS["dark"]["primary"]
            try:
                # Intentar configurar estilo específico
                style = ttk.Style()
                style.configure(f"{style_name}.TButton", background=color, foreground="white")
                style.map(f"{style_name}.TButton", background=[("active", color)])
                button.configure(style=f"{style_name}.TButton")
            except:
                pass
        return button

def create_themed_label(parent, text, style_name="primary", **kwargs):
    """Crea una etiqueta con el estilo especificado"""
    if USING_TTKBOOTSTRAP:
        try:
            return ttk.Label(parent, text=text, bootstyle=style_name, **kwargs)
        except:
            return ttk.Label(parent, text=text, **kwargs)
    else:
        label = ttk.Label(parent, text=text, **kwargs)
        if active_theme == "dark":
            # Configurar colores en modo oscuro
            label.configure(foreground="white", background="#2d2d30")
        return label

def create_themed_frame(parent, style_name="primary", **kwargs):
    """Crea un frame con el estilo especificado"""
    if USING_TTKBOOTSTRAP:
        try:
            return ttk.Frame(parent, bootstyle=style_name, **kwargs)
        except:
            return ttk.Frame(parent, **kwargs)
    else:
        frame = ttk.Frame(parent, **kwargs)
        if active_theme == "dark":
            # Configurar para tema oscuro
            frame.configure(style="dark.TFrame")
        return frame

def apply_theme_to_toplevel(toplevel, theme="dark"):
    """Aplica el tema seleccionado a una ventana Toplevel"""
    if USING_TTKBOOTSTRAP:
        # Si es ttkbootstrap, la ventana heredará el tema
        pass
    else:
        # En modo fallback, aplicar colores manualmente
        colors = COLORS[theme]
        toplevel.configure(bg=colors["bg"])
        
        # Configurar estilos específicos para esta ventana
        style = ttk.Style()
        
        # Configuración agresiva para asegurar tema oscuro
        try:
            # Widgets básicos
            style.configure("TFrame", background=colors["bg"], borderwidth=0)
            style.configure("dark.TFrame", background=colors["bg"], borderwidth=0)
            
            style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
            style.configure("dark.TLabel", background=colors["bg"], foreground=colors["fg"])
            
            # Botones
            style.configure("TButton", background=colors["primary"], foreground="white")
            style.map("TButton", background=[("active", colors["primary"])])
            
            # Pestañas
            style.configure("TNotebook", background=colors["bg"])
            style.configure("TNotebook.Tab", background=colors["secondary"], foreground=colors["fg"])
            style.map("TNotebook.Tab", background=[("selected", colors["primary"])], 
                     foreground=[("selected", "white")])
            
            style.configure("dark.TNotebook", background=colors["bg"])
            style.configure("dark.TNotebook.Tab", background=colors["secondary"], foreground=colors["fg"])
            style.map("dark.TNotebook.Tab", background=[("selected", colors["primary"])], 
                     foreground=[("selected", "white")])
            
            # Scrollbars
            style.configure("Vertical.TScrollbar", background=colors["secondary"], 
                         troughcolor=colors["bg"], bordercolor=colors["secondary"], 
                         arrowcolor=colors["fg"])
            style.map("Vertical.TScrollbar", background=[("active", colors["primary"])])
            
            # LabelFrame
            style.configure("TLabelframe", background=colors["bg"])
            style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["fg"])
            
            # Botones con estilos específicos
            for style_name in ["primary", "secondary", "success", "info", "warning", "danger"]:
                color = colors[style_name]
                style.configure(f"{style_name}.TButton", background=color, foreground="white")
                style.map(f"{style_name}.TButton", background=[("active", color)])
        except Exception as e:
            print(f"Error al aplicar tema a toplevel: {e}")

def create_root_window(title="PokerBot Pro", theme="darkly", size="900x650"):
    """Crea la ventana principal con el tema especificado"""
    global root_window, active_theme
    
    # Guardar el tema activo para uso posterior
    active_theme = "dark" if theme in ["darkly", "superhero", "solar", "cyborg"] else "light"
    
    # Inicializar ttk/ttkbootstrap
    init_ttkbootstrap(theme)
    
    # Crear ventana principal
    root_window = tk.Tk()
    root_window.title(title)
    root_window.geometry(size)
    
    # Configurar colores para modo fallback
    if FALLBACK_MODE:
        colors = COLORS[active_theme]
        root_window.configure(bg=colors["bg"])
        
        # Aplicar tema global
        if active_theme == "dark":
            apply_global_dark_theme()
        
        # Mejorar configuración de estilos para scrollbars y otros widgets
        apply_theme_to_toplevel(root_window, active_theme)
    
    return root_window

def get_themed_style(widget_type, style_name="primary"):
    """Retorna el nombre de estilo adecuado para el contexto actual"""
    if USING_TTKBOOTSTRAP:
        return f"{style_name}"
    else:
        if active_theme == "dark":
            return f"dark.{widget_type}"
        return f"{widget_type}"

def show_message(title, message, message_type="info"):
    """Muestra un mensaje usando el diálogo apropiado"""
    if message_type == "info":
        return messagebox.showinfo(title, message)
    elif message_type == "warning":
        return messagebox.showwarning(title, message)
    elif message_type == "error":
        return messagebox.showerror(title, message)
    elif message_type == "question":
        return messagebox.askyesno(title, message)

def show_toast(title, message, style="success", duration=3000):
    """Muestra una notificación tipo toast (o fallback a messagebox si no está disponible)"""
    try:
        if USING_TTKBOOTSTRAP:
            # Intentar usar ToastNotification si está disponible
            try:
                from ttkbootstrap.toast import ToastNotification
                ToastNotification(
                    title=title,
                    message=message,
                    duration=duration,
                    bootstyle=style
                ).show_toast()
                return
            except ImportError:
                # Si no está disponible, intentar usar en otras ubicaciones conocidas
                pass
                
        # Si no se encuentra ToastNotification o no está usando ttkbootstrap, usar messagebox
        messagebox.showinfo(title, message)
    except Exception:
        # Como último recurso
        tk_messagebox.showinfo(title, message)

# Métodos específicos para trabajar con Tableview en ttkbootstrap 1.13.5
def create_tableview(parent, columns, data=None, height=10, **kwargs):
    """Crea un Tableview o Treeview según la disponibilidad"""
    if USING_TTKBOOTSTRAP:
        try:
            from ttkbootstrap.tableview import Tableview
            
            # Preparar columnas para Tableview
            coldata = []
            for col in columns:
                coldata.append({
                    "text": col["text"] if isinstance(col, dict) else col,
                    "stretch": col.get("stretch", True) if isinstance(col, dict) else True,
                    "width": col.get("width", 100) if isinstance(col, dict) else 100
                })
            
            # Preparar datos
            rowdata = data if data else []
            
            # Crear Tableview
            table = Tableview(
                master=parent,
                coldata=coldata,
                rowdata=rowdata,
                paginated=True,
                searchable=True,
                height=height,
                **kwargs
            )
            
            # Guardar configuración para uso posterior
            table._is_tableview = True
            table.saved_coldata = coldata
            
            return table
        except (ImportError, Exception) as e:
            print(f"Error al crear Tableview: {e}")
            # Fallback a Treeview si falla
            pass
    
    # Crear Treeview estándar como fallback
    column_ids = []
    for i, col in enumerate(columns):
        column_ids.append(f"col{i}" if not isinstance(col, dict) else col.get("id", f"col{i}"))
    
    tree = ttk.Treeview(parent, columns=column_ids, show="headings", height=height)
    
    # Configurar columnas
    for i, col in enumerate(columns):
        col_id = column_ids[i]
        col_text = col["text"] if isinstance(col, dict) else col
        col_width = col.get("width", 100) if isinstance(col, dict) else 100
        
        tree.heading(col_id, text=col_text)
        tree.column(col_id, width=col_width)
    
    # Añadir scrollbar
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    
    # Configuración para tema oscuro
    if active_theme == "dark" and not USING_TTKBOOTSTRAP:
        style = ttk.Style()
        style.configure("Treeview", 
                       background="#2d2d30",
                       foreground="white",
                       fieldbackground="#2d2d30")
        style.configure("Treeview.Heading", 
                       background="#3e3e42",
                       foreground="white")
    
    # Marcar como no Tableview
    tree._is_tableview = False
    
    # Añadir datos si están disponibles
    if data:
        for row in data:
            tree.insert("", "end", values=row)
    
    return tree

def update_tableview(table, data):
    """Actualiza un Tableview o Treeview con nuevos datos"""
    # Limpiar tabla
    if hasattr(table, '_is_tableview') and table._is_tableview:
        try:
            # Para Tableview
            if hasattr(table, 'delete_rows'):
                table.delete_rows()
                
                # Actualizar con nuevos datos
                if hasattr(table, 'build_table_data') and hasattr(table, 'saved_coldata'):
                    table.build_table_data(coldata=table.saved_coldata, rowdata=data)
                    return True
            return False
        except Exception as e:
            print(f"Error al actualizar Tableview: {e}")
            return False
    else:
        # Para Treeview
        try:
            # Limpiar árbol
            for item in table.get_children():
                table.delete(item)
            
            # Añadir nuevos datos
            for row in data:
                table.insert("", "end", values=row)
            
            return True
        except Exception as e:
            print(f"Error al actualizar Treeview: {e}")
            return False