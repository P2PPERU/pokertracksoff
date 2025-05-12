import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
from src.utils.logger import log_message
from src.config.settings import save_config
from src.utils.windows import find_poker_tables

def create_config_tab(parent, config):
    """Crea la pestaña de configuración"""
    # Crear canvas con scroll
    canvas = tk.Canvas(parent)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    
    # Frame principal
    frame_scroll = ttk.Frame(canvas)
    frame_scroll.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Sección de configuración general
    frame_general = ttk.LabelFrame(frame_scroll, text="Configuración General", padding=10)
    frame_general.pack(fill="x", padx=10, pady=5)
    
    # API Key y Token
    ttk.Label(frame_general, text="API Key OpenAI:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_api_key = ttk.Entry(frame_general, width=40)
    entry_api_key.insert(0, config["openai_api_key"])
    entry_api_key.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(frame_general, text="Token de la API:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_token = ttk.Entry(frame_general, width=40)
    entry_token.insert(0, config["token"])
    entry_token.grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(frame_general, text="URL del Servidor:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_server = ttk.Entry(frame_general, width=40)
    entry_server.insert(0, config["server_url"])
    entry_server.grid(row=2, column=1, padx=5, pady=5)
    
    ttk.Label(frame_general, text="Sala por Defecto:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_sala = ttk.Entry(frame_general, width=10)
    entry_sala.insert(0, config["sala_default"])
    entry_sala.grid(row=3, column=1, sticky="w", padx=5, pady=5)
    
    # Hotkey
    ttk.Label(frame_general, text="Hotkey:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    entry_hotkey = ttk.Entry(frame_general, width=10)
    entry_hotkey.insert(0, config["hotkey"])
    entry_hotkey.grid(row=4, column=1, sticky="w", padx=5, pady=5)
    
    # Modo automático
    auto_var = tk.BooleanVar(value=config["modo_automatico"])
    ttk.Label(frame_general, text="Modo Automático:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
    check_auto = ttk.Checkbutton(frame_general, variable=auto_var)
    check_auto.grid(row=5, column=1, sticky="w", padx=5, pady=5)
    
    ttk.Label(frame_general, text="Intervalo de Comprobación (seg):").grid(row=6, column=0, sticky="w", padx=5, pady=5)
    entry_interval = ttk.Entry(frame_general, width=10)
    entry_interval.insert(0, str(config["auto_check_interval"]))
    entry_interval.grid(row=6, column=1, sticky="w", padx=5, pady=5)
    
    # Tema
    ttk.Label(frame_general, text="Tema:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
    tema_var = tk.StringVar(value=config["tema"])
    combo_tema = ttk.Combobox(frame_general, textvariable=tema_var, values=["light", "dark"], width=10)
    combo_tema.grid(row=7, column=1, sticky="w", padx=5, pady=5)
    
    # Idioma OCR
    ttk.Label(frame_general, text="Idioma OCR:").grid(row=8, column=0, sticky="w", padx=5, pady=5)
    ocr_lang_var = tk.StringVar(value=config.get("idioma_ocr", "ch"))
    combo_ocr_lang = ttk.Combobox(frame_general, textvariable=ocr_lang_var, 
                                values=["ch", "en", "jp", "kr", "multilingual"], width=10)
    combo_ocr_lang.grid(row=8, column=1, sticky="w", padx=5, pady=5)
    
    # Sección de coordenadas OCR
    frame_ocr = ttk.LabelFrame(frame_scroll, text="Coordenadas OCR", padding=10)
    frame_ocr.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(frame_ocr, text="X:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_ocr_x = ttk.Entry(frame_ocr, width=10)
    entry_ocr_x.insert(0, str(config["ocr_coords"]["x"]))
    entry_ocr_x.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
    ttk.Label(frame_ocr, text="Y:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_ocr_y = ttk.Entry(frame_ocr, width=10)
    entry_ocr_y.insert(0, str(config["ocr_coords"]["y"]))
    entry_ocr_y.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    
    ttk.Label(frame_ocr, text="Ancho:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_ocr_w = ttk.Entry(frame_ocr, width=10)
    entry_ocr_w.insert(0, str(config["ocr_coords"]["w"]))
    entry_ocr_w.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    
    ttk.Label(frame_ocr, text="Alto:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_ocr_h = ttk.Entry(frame_ocr, width=10)
    entry_ocr_h.insert(0, str(config["ocr_coords"]["h"]))
    entry_ocr_h.grid(row=3, column=1, sticky="w", padx=5, pady=5)
    
    # Función para calibrar OCR
    def calibrate_ocr():
        messagebox.showinfo("Calibración OCR", 
                           "Posiciona el cursor sobre la esquina superior izquierda del área donde aparece el nick "
                           "y presiona Ctrl+1.\nLuego, posiciona el cursor sobre la esquina inferior derecha y "
                           "presiona Ctrl+2.")
        
        # Variables para coordenadas
        coords = {"x1": 0, "y1": 0, "x2": 0, "y2": 0}
        
        def on_ctrl_1():
            import pyautogui
            x, y = pyautogui.position()
            coords["x1"] = x
            coords["y1"] = y
            messagebox.showinfo("Posición 1", f"Posición 1 registrada: ({x}, {y})")
        
        def on_ctrl_2():
            import pyautogui
            x, y = pyautogui.position()
            coords["x2"] = x
            coords["y2"] = y
            messagebox.showinfo("Posición 2", f"Posición 2 registrada: ({x}, {y})")
            
            # Calcular coordenadas relativas
            tables = find_poker_tables()
            if not tables:
                messagebox.showwarning("Error", "No se encontraron mesas para calibrar")
                return
                
            hwnd, _ = tables[0]
            left, top, _, _ = win32gui.GetWindowRect(hwnd)
            
            # Coordenadas relativas
            x_rel = coords["x1"] - left
            y_rel = coords["y1"] - top
            w_rel = coords["x2"] - coords["x1"]
            h_rel = coords["y2"] - coords["y1"]
            
            # Actualizar campos
            entry_ocr_x.delete(0, tk.END)
            entry_ocr_x.insert(0, str(x_rel))
            
            entry_ocr_y.delete(0, tk.END)
            entry_ocr_y.insert(0, str(y_rel))
            
            entry_ocr_w.delete(0, tk.END)
            entry_ocr_w.insert(0, str(w_rel))
            
            entry_ocr_h.delete(0, tk.END)
            entry_ocr_h.insert(0, str(h_rel))
            
            messagebox.showinfo("Calibración completa", 
                               f"Coordenadas actualizadas: X:{x_rel}, Y:{y_rel}, W:{w_rel}, H:{h_rel}")
            
            # Eliminar hotkeys
            keyboard.remove_hotkey('ctrl+1')
            keyboard.remove_hotkey('ctrl+2')
        
        # Registrar hotkeys temporales
        keyboard.add_hotkey('ctrl+1', on_ctrl_1)
        keyboard.add_hotkey('ctrl+2', on_ctrl_2)
    
    ttk.Button(frame_ocr, text="Calibrar OCR",
              command=calibrate_ocr).grid(row=4, column=0, columnspan=2, padx=5, pady=10)
    
    # Botones de guardar/cancelar
    frame_buttons = ttk.Frame(frame_scroll, padding=10)
    frame_buttons.pack(fill="x", padx=10, pady=10)
    
    def save_settings():
        try:
            # Actualizar configuración
            config["openai_api_key"] = entry_api_key.get()
            config["token"] = entry_token.get()
            config["server_url"] = entry_server.get()
            config["sala_default"] = entry_sala.get()
            config["hotkey"] = entry_hotkey.get()
            config["modo_automatico"] = auto_var.get()
            config["auto_check_interval"] = int(entry_interval.get())
            config["tema"] = tema_var.get()
            config["idioma_ocr"] = ocr_lang_var.get()
            
            # Actualizar coordenadas OCR
            config["ocr_coords"] = {
                "x": int(entry_ocr_x.get()),
                "y": int(entry_ocr_y.get()),
                "w": int(entry_ocr_w.get()),
                "h": int(entry_ocr_h.get())
            }
            
            # Guardar configuración
            if save_config(config):
                messagebox.showinfo("Éxito", "Configuración guardada correctamente")
                
                # Preguntar por reinicio
                if messagebox.askyesno("Reiniciar", 
                                      "Algunos cambios requieren reiniciar la aplicación. "
                                      "¿Deseas reiniciar ahora?"):
                    # Código para reiniciar la aplicación
                    from src.ui.main_window import root
                    root.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar la configuración")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {e}")
            log_message(f"Error al guardar configuración: {e}", level='error')
    
    ttk.Button(frame_buttons, text="Guardar Cambios", 
              command=save_settings).pack(side="right", padx=5)
    
    ttk.Button(frame_buttons, text="Cancelar", 
              command=lambda: parent.select(0)).pack(side="right", padx=5)
    
    return frame_scroll