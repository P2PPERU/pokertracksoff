import os
import time
import numpy as np
from PIL import Image, ImageDraw
from paddleocr import PaddleOCR
import pyautogui
import win32gui
import win32api
import win32con

# Variables globales para OCR
ocr = None
ocr_initialized = False

def initialize_ocr(config):
    """Inicializa el motor OCR y lo pre-calienta con una imagen de prueba"""
    global ocr, ocr_initialized
    
    try:
        ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            det_db_thresh=0.3,
            show_log=False,
            rec_batch_num=1,
            use_gpu=True
        )
        
        # Pre-calentar OCR con una imagen de prueba
        create_and_test_ocr_sample()
        
        return True
    except Exception as e:
        print(f"Error al inicializar OCR: {e}")
        return False

def create_and_test_ocr_sample():
    """Crea y prueba una imagen de muestra para pre-inicializar el OCR"""
    global ocr_initialized
    
    try:
        # Crear una imagen de prueba con caracteres asiáticos
        img = Image.new('RGB', (150, 40), color=(0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Test OCR 测试 テスト", fill=(255, 255, 255))
        
        # Guardar temporalmente
        test_img_path = "capturas/test_ocr.png"
        img.save(test_img_path)
        
        # Ejecutar OCR en la imagen de prueba
        img_np = np.array(img)
        result = ocr.ocr(img_np, cls=True)
        
        # Si llegamos aquí, OCR está inicializado
        ocr_initialized = True
        return True
    except Exception as e:
        print(f"Error en pre-inicialización OCR: {e}")
        return False

def capture_and_read_nick(hwnd, coords):
    """Captura y lee el nick de un jugador usando OCR"""
    try:
        # Obtener coordenadas de la ventana
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        region = (left + coords["x"], top + coords["y"], coords["w"], coords["h"])
        
        # Clic en el área para activar la visualización del nick
        x_click = left + coords["x"] + 10
        y_click = top + coords["y"] + 10
        
        # Clic sin mover el cursor visible
        win32api.SendMessage(
            hwnd, 
            win32con.WM_LBUTTONDOWN, 
            win32con.MK_LBUTTON, 
            win32api.MAKELONG(x_click - left, y_click - top)
        )
        time.sleep(0.05)
        win32api.SendMessage(
            hwnd, 
            win32con.WM_LBUTTONUP, 
            0, 
            win32api.MAKELONG(x_click - left, y_click - top)
        )
        time.sleep(0.1)
        
        # Capturar imagen
        img = pyautogui.screenshot(region=region)
        timestamp = time.strftime("%H%M%S")
        debug_path = f"capturas/capture_{timestamp}.png"
        img.save(debug_path)
        
        # Procesar con OCR
        img_np = np.array(img)
        result = ocr.ocr(img_np, cls=True)
        
        # Extraer texto detectado
        if result and result[0]:
            detected_texts = []
            for line in result:
                for word in line:
                    text = word[1][0].strip()
                    confidence = word[1][1]
                    if text and len(text) > 0:
                        detected_texts.append((text, confidence))
            
            if detected_texts:
                # Ordenar por confianza
                sorted_texts = sorted(detected_texts, key=lambda x: x[1], reverse=True)
                final_nick = sorted_texts[0][0][:25].strip()
                return final_nick
        
        return None
    except Exception as e:
        print(f"Error en OCR: {e}")
        return None