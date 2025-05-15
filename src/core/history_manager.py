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
            log_message("Archivo de historial no encontrado, se creó uno nuevo")
            return []
        
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                log_message("Archivo de historial está vacío")
                return []
                
            history = json.loads(content)
            if not isinstance(history, list):
                log_message("Error: El archivo de historial no contiene una lista válida", level='error')
                return []
                
            log_message(f"Historial cargado: {len(history)} entradas")
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
                
                # Crear un nuevo archivo vacío
                with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                    f.write("[]")
                log_message("Se creó un nuevo archivo de historial vacío")
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
    """Añade una entrada al historial, reemplazando entradas existentes del mismo jugador si los stats cambiaron"""
    try:
        history = load_history()
        log_message(f"Historial cargado para agregar entrada: {len(history)} entradas existentes")
        
        # Extraer información de la entrada actual
        current_nick = entry.get("nick", "")
        current_stats = entry.get("stats", "")
        current_sala = entry.get("sala", "")
        
        # Buscar si el jugador ya existe en el historial
        existing_index = None
        
        for i, hist_entry in enumerate(history):
            if hist_entry.get("nick") == current_nick and hist_entry.get("sala") == current_sala:
                existing_index = i
                break
        
        # Si el jugador existe, verificar si los stats son diferentes
        if existing_index is not None:
            existing_stats = history[existing_index].get("stats", "")
            
            if existing_stats == current_stats:
                # Los stats son iguales, no hacer nada
                log_message(f"Jugador {current_nick} ya existe con los mismos stats, no se agrega al historial")
                return True
            else:
                # Los stats son diferentes, reemplazar la entrada
                log_message(f"Actualizando stats para jugador {current_nick}")
                history[existing_index] = entry
        else:
            # El jugador no existe, agregar nueva entrada
            history.append(entry)
        
        success = save_history(history)
        
        if success:
            log_message(f"Entrada añadida/actualizada en el historial. Total: {len(history)} entradas")
        else:
            log_message("No se pudo guardar la entrada en el historial", level='warning')
        
        return success
    except Exception as e:
        log_message(f"Error al añadir entrada al historial: {e}", level='error')
        import traceback
        log_message(traceback.format_exc(), level='error')
        return False
    
def find_existing_analysis(nick, stats, sala):
    """Busca un análisis existente para un jugador con stats idénticos"""
    try:
        history = load_history()
        
        for entry in history:
            if (entry.get("nick") == nick and 
                entry.get("stats") == stats and 
                entry.get("sala") == sala and
                "analisis" in entry and entry["analisis"]):
                
                log_message(f"Análisis existente encontrado para {nick} con los mismos stats")
                return entry["analisis"]
        
        return None
    except Exception as e:
        log_message(f"Error al buscar análisis existente: {e}", level='error')
        return None


def clear_history():
    """Limpia todo el historial"""
    try:
        save_history([])
        log_message("Historial limpiado completamente")
        return True
    except Exception as e:
        log_message(f"Error al limpiar historial: {e}", level='error')
        return False