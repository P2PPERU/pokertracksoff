import os
import time
import numpy as np
from PIL import Image, ImageDraw
from paddleocr import PaddleOCR
import win32gui
import win32api
import win32con
import win32ui
from src.utils.logger import log_message  # Añadir esta importación

# Variables globales para OCR
ocr = None
ocr_initialized = False

def initialize_ocr(config):
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
        create_and_test_ocr_sample()
        return True
    except Exception as e:
        print(f"Error al inicializar OCR: {e}")
        return False

def create_and_test_ocr_sample():
    global ocr_initialized
    try:
        img = Image.new('RGB', (150, 40), color=(0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Test OCR 测试 テスト", fill=(255, 255, 255))
        test_img_path = "capturas/test_ocr.png"
        img.save(test_img_path)
        img_np = np.array(img)
        result = ocr.ocr(img_np, cls=True)
        ocr_initialized = True
        log_message("OCR pre-inicializado correctamente con prueba de caracteres asiáticos")
        return True
    except Exception as e:
        log_message(f"Error en pre-inicialización OCR: {e}", level='error')
        return False

def capture_window_region(hwnd, region):
    """Captura una región de una ventana usando GDI y la devuelve como PIL Image"""
    x, y, w, h = region
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (x, y), win32con.SRCCOPY)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img

def capture_and_read_nick(hwnd, coords, retry=True):
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        region = (coords["x"], coords["y"], coords["w"], coords["h"])
        abs_region = (left + region[0], top + region[1], region[2], region[3])

        # Clic en la zona del nick
        x_click = abs_region[0] + 10
        y_click = abs_region[1] + 10
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(x_click - left, y_click - top))
        time.sleep(0.05)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(x_click - left, y_click - top))
        time.sleep(0.1)

        # Capturar imagen con método GDI
        img = capture_window_region(hwnd, region)
        timestamp = time.strftime("%H%M%S")
        debug_path = f"capturas/capture_{timestamp}.png"
        img.save(debug_path)

        img_np = np.array(img)
        detected_texts = []

        # 1. PaddleOCR
        try:
            result = ocr.ocr(img_np, cls=True)
            if result and result[0]:
                for line in result:
                    for word in line:
                        text = word[1][0].strip()
                        confidence = word[1][1]
                        if text:
                            detected_texts.append((text, confidence))
                            log_message(f"PaddleOCR detectó: '{text}' (confianza: {confidence:.2f})")
        except Exception as e:
            log_message(f"Error en PaddleOCR: {e}", level='error')

        # 2. Tesseract si falló
        if not detected_texts:
            try:
                import pytesseract
                custom_config = r'--oem 3 --psm 7 -l chi_sim+jpn+kor+eng'
                texto = pytesseract.image_to_string(img, config=custom_config)
                if texto.strip():
                    detected_texts.append((texto.strip(), 0.8))
                    log_message(f"Tesseract detectó: '{texto.strip()}'")
            except Exception as e:
                log_message(f"Error en Tesseract: {e}", level='error')

        # 3. Segundo intento si aún no hay resultados
        if not detected_texts and retry:
            log_message("Realizando segundo intento con nuevo clic")
            from src.utils.windows import click_on_window_point
            click_on_window_point(hwnd, coords["x"] + 10, coords["y"] + 10)
            time.sleep(0.2)
            return capture_and_read_nick(hwnd, coords, retry=False)

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
