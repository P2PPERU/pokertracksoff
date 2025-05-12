#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PokerBot Pro - Sistema de análisis de estadísticas para jugadores de poker
"""

import os
import sys
import time
import threading
import tkinter as tk
from pynput.mouse import Listener, Button

from src.utils.logger import setup_logger, log_message
from src.config.settings import load_config, save_config
from src.ui.main_window import create_main_window, root, running, auto_running, update_ui_status
from src.core.ocr_engine import initialize_ocr
from src.core.poker_analyzer import analyze_table, clear_nick_cache
from src.utils.windows import get_window_under_cursor, find_poker_tables, focus_window

# Variables globales
mouse_listener = None

def on_right_click(x, y, button, pressed):
    """Maneja el evento de clic derecho para analizar mesa bajo el cursor"""
    global running
    
    if not running:
        return False
        
    if button == Button.right and pressed:
        log_message("Clic derecho detectado, buscando mesa bajo el cursor")
        hwnd, title = get_window_under_cursor()
        
        if hwnd:
            log_message(f"Mesa encontrada: {title}")
            
            # Crear hilo para análisis para no bloquear el listener de eventos
            config = load_config()
            threading.Thread(target=analyze_table, args=(hwnd, config)).start()
        else:
            log_message("No se encontró una mesa bajo el cursor", level='warning')
    
    return True  # Continuar con el listener

def start_right_click_listener():
    """Inicia el listener de clic derecho"""
    global mouse_listener
    
    try:
        log_message("Iniciando listener de clic derecho")
        mouse_listener = Listener(on_click=on_right_click)
        mouse_listener.daemon = True
        mouse_listener.start()
        return mouse_listener
    except Exception as e:
        log_message(f"Error al iniciar listener de clic derecho: {e}", level='error')
        return None

def stop_right_click_listener():
    """Detiene el listener de clic derecho"""
    global mouse_listener
    
    if mouse_listener and mouse_listener.is_alive():
        log_message("Deteniendo listener de clic derecho")
        mouse_listener.stop()
        mouse_listener = None

def auto_mode_loop(config):
    """Bucle principal del modo automático"""
    global running, auto_running
    
    log_message("Iniciando bucle automático")
    
    while auto_running and running:
        try:
            tables = find_poker_tables()
            if tables:
                for hwnd, title in tables:
                    if not auto_running or not running:
                        break
                    
                    log_message(f"Procesando mesa automáticamente: {title}")
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

def start_auto_mode(config):
    """Inicia el modo automático"""
    global auto_running
    
    if auto_running:
        log_message("El modo automático ya está en ejecución")
        return
    
    auto_running = True
    threading.Thread(target=auto_mode_loop, args=(config,), daemon=True).start()
    log_message("Modo automático iniciado")
    
    # Actualizar UI si está disponible
    if 'root' in globals() and root and root.winfo_exists():
        update_ui_status()

def stop_auto_mode():
    """Detiene el modo automático"""
    global auto_running
    
    if not auto_running:
        log_message("El modo automático no está en ejecución")
        return
    
    auto_running = False
    log_message("Deteniendo modo automático...")
    
    # Actualizar UI si está disponible
    if 'root' in globals() and root and root.winfo_exists():
        update_ui_status()

def on_exit():
    """Función que se ejecuta al cerrar la aplicación"""
    global running, auto_running, mouse_listener
    
    log_message("Cerrando aplicación...")
    
    # Detener procesos en segundo plano
    running = False
    auto_running = False
    
    # Detener listener de clic derecho
    stop_right_click_listener()
    
    # Guardar configuración y datos finales
    try:
        config = load_config()
        save_config(config)
    except Exception as e:
        log_message(f"Error al guardar configuración: {e}", level='error')
    
    log_message("Aplicación cerrada correctamente")

def register_hotkey(config):
    """Registra el hotkey global"""
    try:
        import keyboard
        
        def hotkey_handler():
            log_message(f"Hotkey {config['hotkey']} activado")
            hwnd, title = get_window_under_cursor()
            
            if hwnd:
                log_message(f"Analizando mesa: {title}")
                analyze_table(hwnd, config)
            else:
                # Sin mesa específica, buscar la primera disponible
                tables = find_poker_tables()
                if tables:
                    hwnd, title = tables[0]
                    log_message(f"Analizando primera mesa disponible: {title}")
                    analyze_table(hwnd, config)
                else:
                    log_message("No se encontró ninguna mesa activa", level='warning')
        
        # Registrar hotkey
        keyboard.add_hotkey(config["hotkey"], hotkey_handler)
        log_message(f"Hotkey {config['hotkey']} registrado correctamente")
        return True
    except Exception as e:
        log_message(f"Error al registrar hotkey: {e}", level='error')
        return False

def main():
    """Función principal que inicia la aplicación"""
    global running
    
    try:
        # Crear carpetas necesarias
        os.makedirs("logs", exist_ok=True)
        os.makedirs("capturas", exist_ok=True)
        os.makedirs("config", exist_ok=True)
        
        # Configurar logger
        logger = setup_logger()
        log_message("Iniciando PokerBot Pro...")
        
        # Cargar configuración
        config = load_config()
        
        # Inicializar OCR
        if not initialize_ocr(config):
            log_message("Error al inicializar OCR. Las funciones de lectura pueden fallar.", level='warning')
        
        # Iniciar listener de clic derecho
        start_right_click_listener()
        
        # Registrar hotkey global
        register_hotkey(config)
        
        # Inicializar running
        running = True
        
        # Crear y ejecutar la interfaz de usuario
        create_main_window(config)
        
        # Iniciar modo automático si está configurado
        if config["modo_automatico"]:
            start_auto_mode(config)
        
        # Mostrar mensaje de bienvenida
        log_message("=== PokerBot Pro iniciado correctamente ===")
        log_message(f"Presiona {config['hotkey']} o haz clic derecho para analizar nick")
        
        # Si tenemos interfaz gráfica, entramos en el mainloop de Tk
        if 'root' in globals() and root:
            root.protocol("WM_DELETE_WINDOW", on_exit)
            root.mainloop()
        
        # Si no hay UI o se cerró, también ejecutamos on_exit
        on_exit()
        
    except Exception as e:
        log_message(f"Error crítico en la aplicación: {e}", level='critical')
        import traceback
        log_message(traceback.format_exc(), level='critical')
        sys.exit(1)

if __name__ == "__main__":
    main()