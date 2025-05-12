import tkinter as tk
from tkinter import ttk

def create_logs_tab(parent):
    """Crea la pestaña de logs"""
    # Crear frame principal
    tab = ttk.Frame(parent)
    tab.name = "tab_logs"
    
    # Área de texto para logs
    log_text = tk.Text(tab, wrap="word")
    log_text.pack(fill="both", expand=True, padx=10, pady=10)
    log_text.config(state="disabled")
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(log_text, orient="vertical", command=log_text.yview)
    log_text.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    
    # Botón para limpiar logs
    def clear_logs():
        log_text.config(state="normal")
        log_text.delete("1.0", tk.END)
        log_text.config(state="disabled")
    
    ttk.Button(tab, text="Limpiar Logs", command=clear_logs).pack(padx=10, pady=5)
    
    return tab

def update_logs_text(log_text, message):
    """Actualiza el área de texto de logs con un nuevo mensaje"""
    if not log_text or not log_text.winfo_exists():
        return
        
    log_text.config(state="normal")
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)
    log_text.config(state="disabled")