import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configuración por defecto
DEFAULT_CONFIG = {
    "token": "",  # será reemplazado desde .env
    "openai_api_key": "",  # será reemplazado desde .env
    "ocr_coords": {"x": 95, "y": 110, "w": 95, "h": 22},
    "server_url": "http://localhost:3000",
    "sala_default": "XPK",
    "hotkey": "alt+q",
    "modo_automatico": False,
    "auto_check_interval": 30,
    "mostrar_stats": True,
    "mostrar_analisis": True,
    "tema": "dark",
    "idioma_ocr": "ch",
    "mostrar_dialogo_copia": False,
    "stats_seleccionadas": {
        "vpip": True, "pfr": True, "three_bet": True, "fold_to_3bet_pct": True,
        "wtsd": True, "wsd": True, "cbet_flop": True, "cbet_turn": True,
        "fold_to_flop_cbet_pct": False, "fold_to_turn_cbet_pct": False,
        "limp_pct": False, "limp_raise_pct": False, "four_bet_preflop_pct": False,
        "fold_to_4bet_pct": False, "probe_bet_turn_pct": False, "bet_river_pct": False,
        "fold_to_river_bet_pct": False, "overbet_turn_pct": False, "overbet_river_pct": False,
        "wsdwbr_pct": False, "wwsf": False, "total_manos": False, "bb_100": False, "win_usd": False
    },
    "stats_order": [
        "vpip", "pfr", "three_bet", "fold_to_3bet_pct", "wtsd", "wsd", "cbet_flop", "cbet_turn",
        "fold_to_flop_cbet_pct", "fold_to_turn_cbet_pct", "four_bet_preflop_pct", "fold_to_4bet_pct",
        "limp_pct", "limp_raise_pct", "probe_bet_turn_pct", "bet_river_pct",
        "fold_to_river_bet_pct", "overbet_turn_pct", "overbet_river_pct", "wsdwbr_pct",
        "wwsf", "total_manos", "bb_100", "win_usd"
    ],
    "stats_format": {
        "vpip": "VPIP:{value}", "pfr": "PFR:{value}", "three_bet": "3B:{value}",
        "fold_to_3bet_pct": "F3B:{value}", "wtsd": "WTSD:{value}", "wsd": "WSD:{value}",
        "cbet_flop": "CF:{value}", "cbet_turn": "CT:{value}", "fold_to_flop_cbet_pct": "FFC:{value}",
        "fold_to_turn_cbet_pct": "FTC:{value}", "limp_pct": "LIMP:{value}", "limp_raise_pct": "LR:{value}",
        "four_bet_preflop_pct": "4B:{value}", "fold_to_4bet_pct": "F4B:{value}", "probe_bet_turn_pct": "PBT:{value}",
        "bet_river_pct": "BR:{value}", "fold_to_river_bet_pct": "FRB:{value}", "overbet_turn_pct": "OBT:{value}",
        "overbet_river_pct": "OBR:{value}", "wsdwbr_pct": "WBR:{value}", "wwsf": "WWSF:{value}",
        "total_manos": "Manos:{value}", "bb_100": "BB/100:{value}", "win_usd": "USD:{value}"
    }
}

CONFIG_PATH = Path("config/config.json")

def load_config():
    """Carga la configuración desde el archivo config.json y el entorno"""
    try:
        config = DEFAULT_CONFIG.copy()

        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config_loaded = json.load(f)
                
                for key, value in config_loaded.items():
                    if key in config:
                        if isinstance(config[key], dict) and isinstance(value, dict):
                            config[key].update(value)
                        else:
                            config[key] = value
                    else:
                        config[key] = value

        # Validaciones de stats
        for stat in config["stats_order"]:
            if stat not in config["stats_seleccionadas"]:
                config["stats_seleccionadas"][stat] = False
        for stat in config["stats_seleccionadas"]:
            if stat not in config["stats_order"]:
                config["stats_order"].append(stat)
        for stat in config["stats_seleccionadas"]:
            if stat not in config["stats_format"]:
                config["stats_format"][stat] = f"{stat.upper()}:{{value}}"

        # ⚠️ Cargar valores sensibles desde .env
        config["token"] = os.getenv("TOKEN", "")
        config["openai_api_key"] = os.getenv("OPENAI_API_KEY", "")

        return config

    except Exception as e:
        print(f"Error al cargar configuración: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Guarda la configuración en el archivo config.json"""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False

def reset_config():
    """Restablece la configuración a los valores por defecto"""
    try:
        save_config(DEFAULT_CONFIG.copy())
        return True
    except Exception as e:
        print(f"Error al restablecer configuración: {e}")
        return False

def get_stat_display_name(stat_key):
    """Obtiene el nombre para mostrar de una estadística"""
    stat_display_names = {
        "vpip": "VPIP", "pfr": "PFR", "three_bet": "3-Bet", "fold_to_3bet_pct": "Fold to 3-Bet",
        "wtsd": "WTSD", "wsd": "WSD", "cbet_flop": "C-Bet Flop", "cbet_turn": "C-Bet Turn",
        "fold_to_flop_cbet_pct": "Fold to Flop C-Bet", "fold_to_turn_cbet_pct": "Fold to Turn C-Bet",
        "limp_pct": "Limp %", "limp_raise_pct": "Limp-Raise %", "four_bet_preflop_pct": "4-Bet Preflop",
        "fold_to_4bet_pct": "Fold to 4-Bet", "probe_bet_turn_pct": "Probe Bet Turn", "bet_river_pct": "Bet River",
        "fold_to_river_bet_pct": "Fold to River Bet", "overbet_turn_pct": "Overbet Turn",
        "overbet_river_pct": "Overbet River", "wsdwbr_pct": "WSD with Bet River", "wwsf": "WWSF",
        "total_manos": "Total Manos", "bb_100": "BB/100", "win_usd": "Ganancias USD"
    }
    return stat_display_names.get(stat_key, stat_key.upper())
