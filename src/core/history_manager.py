import json
import os
from pathlib import Path
from src.utils.logger import log_message

HISTORY_PATH = Path("config/historial.json")

def load_history():
    """Carga el historial de búsquedas desde el archivo"""
    try:
        if not HISTORY_PATH.exists():
            # Crear archivo vacío si no existe
            HISTORY_PATH.parent.mkdir(exist_ok=True)
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                f.write("[]")
            return []
        
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return []
                
            history = json.loads(content)
            if not isinstance(history, list):
                log_message("Error: El archivo de historial no contiene una lista válida")
                return []
                
            return history
    except json.JSONDecodeError as e:
        log_message(f"Error al decodificar JSON del historial: {e}", level='error')
        # Crear copia de seguridad del archivo corrupto
        if HISTORY_PATH.exists():
            from datetime import datetime
            backup_name = f"config/historial_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                import shutil
                shutil.copy(HISTORY_PATH, backup_name)
                log_message(f"Copia de seguridad creada: {backup_name}")
            except Exception as backup_error:
                log_message(f"Error al crear copia de seguridad: {backup_error}", level='error')
        return []
    except Exception as e:
        log_message(f"Error al cargar historial: {e}", level='error')
        import traceback
        log_message(traceback.format_exc(), level='error')
        return []

def save_history(history):
    """Guarda el historial en el archivo"""
    try:
        # Verificar que es una lista
        if not isinstance(history, list):
            log_message("Advertencia: Historial no es una lista. Inicializando.", level='warning')
            history = []
        
        # Limitar a 100 entradas más recientes
        limited_history = history[-100:] if len(history) > 100 else history
        
        # Guardar en archivo
        HISTORY_PATH.parent.mkdir(exist_ok=True)
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(limited_history, f, indent=4, ensure_ascii=False)
            
        log_message(f"Historial guardado: {len(limited_history)} entradas")
        return True
    except Exception as e:
        log_message(f"Error al guardar historial: {e}", level='error')
        import traceback
        log_message(traceback.format_exc(), level='error')
        return False

def add_to_history(entry):
    """Añade una entrada al historial"""
    history = load_history()
    history.append(entry)
    save_history(history)
    return True

def clear_history():
    """Limpia todo el historial"""
    save_history([])
    log_message("Historial limpiado completamente")
    return True