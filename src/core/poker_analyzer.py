import time
import threading
import pyperclip
import pyautogui
from datetime import datetime

from src.utils.logger import log_message
from src.utils.windows import focus_window, get_window_under_cursor
from src.core.ocr_engine import capture_and_read_nick
from src.core.api_client import get_player_stats
from src.core.gpt_client import analyze_stats
from src.core.history_manager import add_to_history, load_history
from src.utils.image_utils import generate_image_hash

# Caché de nicks y hashes
nick_cache = {}
last_nick_data = {}

def clear_nick_cache():
    """Limpia la caché de nicks detectados"""
    global nick_cache, last_nick_data
    nick_cache = {}
    last_nick_data = {}
    log_message("Caché de nicks limpiada")

def paste_to_poker(text):
    """Pega texto en la ventana activa de poker"""
    try:
        pyperclip.copy(text)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")
        log_message("Texto pegado en ventana de poker")
        return True
    except Exception as e:
        log_message(f"Error al pegar texto: {e}", level='error')
        return False

def format_stats_summary(data):
    """Formatea las estadísticas principales en formato corto"""
    try:
        return (f"VPIP:{int(float(data['vpip']))} PFR:{int(float(data['pfr']))} "
                f"3B:{int(float(data['three_bet']))} F3B:{int(float(data['fold_to_3bet_pct']))} "
                f"WTSD:{int(float(data['wtsd']))} WSD:{int(float(data['wsd']))} "
                f"CB:{int(float(data['cbet_flop']))}/{int(float(data['cbet_turn']))}")
    except Exception as e:
        log_message(f"Error al formatear stats: {e}", level='error')
        return "Error al formatear stats"

def analyze_table(hwnd, config, manual_nick=None, force_new_capture=False):
    """Función principal para analizar una mesa de poker"""
    global nick_cache, last_nick_data
    
    try:
        log_message("Iniciando análisis de mesa")
        
        # 1. Determinar el nick del jugador
        if manual_nick:
            # Usar nick manual proporcionado
            nick = manual_nick
            log_message(f"Usando nick manual: '{nick}'")
        else:
            # Decidir si usar caché o capturar de nuevo
            use_cache = not force_new_capture and hwnd in nick_cache and (time.time() - nick_cache[hwnd]["timestamp"]) < 300
            
            if use_cache:
                # Verificar si el jugador cambió mediante hash de la imagen
                from src.utils.windows import win32gui
                left, top, _, _ = win32gui.GetWindowRect(hwnd)
                coords = config["ocr_coords"]
                region = (left + coords["x"], top + coords["y"], coords["w"], coords["h"])
                
                # Capturar imagen para comparación
                img = pyautogui.screenshot(region=region)
                img_hash = generate_image_hash(img)
                
                # Comparar con hash anterior si existe
                if hwnd in last_nick_data and "img_hash" in last_nick_data[hwnd]:
                    if img_hash != last_nick_data[hwnd]["img_hash"]:
                        log_message("Detectado cambio de jugador en la misma ventana")
                        use_cache = False  # Forzar nueva captura
                
                if use_cache:
                    nick = nick_cache[hwnd]["nick"]
                    log_message(f"Nick recuperado de caché: '{nick}'")
                else:
                    log_message("La ventana cambió, obteniendo nuevo nick...")
            
            # Si no usamos caché, capturar nuevo nick
            if not use_cache:
                # Activar ventana y capturar nick
                original_hwnd, current_hwnd = focus_window(hwnd)
                
                # Leer nick usando OCR
                log_message("Leyendo nick...")
                nick = capture_and_read_nick(hwnd, config["ocr_coords"])
                
                if not nick:
                    log_message("No se detectó ningún nick", level='warning')
                    return False
                
                # Actualizar caché
                nick_cache[hwnd] = {
                    "nick": nick,
                    "timestamp": time.time()
                }
                
                # Actualizar hash de imagen
                left, top, _, _ = win32gui.GetWindowRect(hwnd)
                coords = config["ocr_coords"]
                region = (left + coords["x"], top + coords["y"], coords["w"], coords["h"])
                img = pyautogui.screenshot(region=region)
                img_hash = generate_image_hash(img)
                
                log_message(f"Nick detectado: '{nick}'")
        
        # 2. Obtener estadísticas del jugador
        try:
            stats_data = get_player_stats(nick, config["sala_default"], config["token"], config["server_url"])
            
            # Actualizar datos de último nick
            last_nick_data[hwnd] = {
                "nick": nick,
                "img_hash": img_hash if 'img_hash' in locals() else None
            }
            
            # Añadir nick a los datos
            stats_data["player_name"] = nick
            
            # 3. Formatear estadísticas y generar análisis
            stats_summary = format_stats_summary(stats_data)
            analysis = analyze_stats(stats_data, config["openai_api_key"], nick)
            
            log_message(f"Stats: {stats_summary}")
            log_message(f"Análisis: {analysis[:100]}...")  # Primeros 100 caracteres
            
            # 4. Preparar resultado final
            result = ""
            if config["mostrar_stats"]:
                result += f"{stats_summary}\n"
            if config["mostrar_analisis"]:
                result += f"{analysis}"
            
            if not result:
                log_message("No hay contenido para mostrar según la configuración")
                return False
            
            # 5. Pegar resultado en la mesa
            success = paste_to_poker(result)
            
            # 6. Guardar en historial
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_entry = {
                "timestamp": timestamp,
                "nick": nick,
                "stats": stats_summary,
                "analisis": analysis,
                "sala": config["sala_default"]
            }
            
            add_to_history(history_entry)
            
            # 7. Actualizar UI si es necesario
            if hasattr(threading, '_threading_main') and threading._threading_main:
                from src.ui.tabs.history_tab import update_history_treeview
                from src.ui.main_window import history_tree
                if history_tree:
                    update_history_treeview(history_tree)
            
            log_message("Análisis completado con éxito")
            return True
            
        except Exception as e:
            log_message(f"Error al obtener/analizar stats: {e}", level='error')
            
            # Limpiar caché en caso de error
            if hwnd in nick_cache:
                del nick_cache[hwnd]
            if hwnd in last_nick_data:
                del last_nick_data[hwnd]
                
            return False
        
    except Exception as e:
        log_message(f"Error en análisis de mesa: {e}", level='error')
        import traceback
        log_message(traceback.format_exc(), level='error')
        return False