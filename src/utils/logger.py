import logging
import os
from datetime import datetime
from pathlib import Path

logger = None

def setup_logger():
    """Configura e inicializa el sistema de logging"""
    global logger
    
    if logger:
        return logger
    
    # Crear logger
    logger = logging.getLogger("PokerBot")
    logger.setLevel(logging.INFO)
    
    # Crear formato
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                 datefmt='%Y-%m-%d %H:%M:%S')
    
    # Crear manejador para la consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Crear manejador para archivo
    log_file = f"logs/pokerbot_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_logger():
    """Obtiene el logger inicializado"""
    global logger
    if not logger:
        logger = setup_logger()
    return logger

def log_message(message, level='info'):
    """Registra un mensaje en el log"""
    logger = get_logger()
    
    level_methods = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical
    }
    
    # Llamar al método de logging correspondiente
    log_func = level_methods.get(level.lower(), logger.info)
    log_func(message)
    
    return message