import os
import time
import numpy as np
from PIL import Image, ImageDraw
from paddleocr import PaddleOCR
import pyautogui
import win32gui
import win32api
import win32con
from src.utils.logger import log_message  # Añadir esta importación

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
        log_message("OCR pre-inicializado correctamente con prueba de caracteres asiáticos")
        return True
    except Exception as e:
        log_message(f"Error en pre-inicialización OCR: {e}", level='error')
        return False

def capture_and_read_nick(hwnd, coords, retry=True):
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
        
        # 1. Primer intento con PaddleOCR
        detected_texts = []
        
        try:
            result = ocr.ocr(img_np, cls=True)
            
            if result and result[0]:
                for line in result:
                    for word in line:
                        text = word[1][0].strip()
                        confidence = word[1][1]
                        if text and len(text) > 0:
                            detected_texts.append((text, confidence))
                            log_message(f"PaddleOCR detectó: '{text}' (confianza: {confidence:.2f})")
        except Exception as e:
            log_message(f"Error en PaddleOCR: {e}", level='error')
        
        # 2. Segundo intento con Tesseract si está disponible y no detectamos nada
        if not detected_texts:
            try:
                import pytesseract
                custom_config = r'--oem 3 --psm 7 -l chi_sim+jpn+kor+eng'
                texto = pytesseract.image_to_string(img, config=custom_config)
                if texto and texto.strip():
                    detected_texts.append((texto.strip(), 0.8))
                    log_message(f"Tesseract detectó: '{texto.strip()}'")
            except ImportError:
                log_message("pytesseract no disponible", level='warning')
            except Exception as e:
                log_message(f"Error en Tesseract: {e}", level='error')
        
        # 3. Tercer intento con un segundo clic si aún no hay resultados
        if not detected_texts and retry:
            log_message("Realizando segundo intento con nuevo clic")
            
            # Clic silencioso en las coordenadas
            from src.utils.windows import click_on_window_point
            click_on_window_point(hwnd, coords["x"] + 10, coords["y"] + 10)
            time.sleep(0.2)
            
            # Intentar de nuevo sin recursión para evitar bucles
            return capture_and_read_nick(hwnd, coords, retry=False)
        
        # Procesar resultados
        if detected_texts:
            sorted_texts = sorted(detected_texts, key=lambda x: x[1], reverse=True)
            final_nick = sorted_texts[0][0][:25].strip()
            log_message(f"Nick final: '{final_nick}'")
            return final_nick
        else:
            log_message("No se pudo detectar ningún nick", level='warning')
            return None
            
    except Exception as e:
        log_message(f"Error en capture_and_read_nick: {e}", level='error')
        import traceback
        log_message(traceback.format_exc(), level='error')
        return None