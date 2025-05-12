#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PokerBot Pro - Sistema de análisis de estadísticas para jugadores de poker
"""

import os
import sys
from src.utils.logger import setup_logger
from src.config.settings import load_config
from src.ui.main_window import create_main_window
from src.core.ocr_engine import initialize_ocr

def main():
    """Función principal que inicia la aplicación"""
    # Crear carpetas necesarias
    os.makedirs("logs", exist_ok=True)
    os.makedirs("capturas", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # Configurar logger
    logger = setup_logger()
    logger.info("Iniciando PokerBot Pro...")
    
    # Cargar configuración
    config = load_config()
    
    # Inicializar OCR
    initialize_ocr(config)
    
    # Crear y ejecutar la interfaz de usuario
    create_main_window(config)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"Error crítico: {e}")
        traceback.print_exc()
        sys.exit(1)