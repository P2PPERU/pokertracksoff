import json
import os
from pathlib import Path

# Configuración por defecto
DEFAULT_CONFIG = {
    "token": "",
    "openai_api_key": "",
    "ocr_coords": {"x": 95, "y": 110, "w": 95, "h": 22},
    "server_url": "http://localhost:3000",
    "sala_default": "XPK",
    "hotkey": "alt+q",
    "modo_automatico": False,
    "auto_check_interval": 30,
    "mostrar_stats": True,
    "mostrar_analisis": True,
    "tema": "dark"
}

CONFIG_PATH = Path("config/config.json")

def load_config():
    """Carga la configuración desde el archivo config.json"""
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config_loaded = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(config_loaded)
                return config
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Guarda la configuración en el archivo config.json"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False