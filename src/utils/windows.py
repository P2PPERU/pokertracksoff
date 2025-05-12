import re
import win32gui
import win32api
import win32con
import pyautogui
import time

def is_poker_table(title):
    """Detecta si una ventana es una mesa de poker"""
    return bool(re.search(r'\d+ *\/ *\d+|\d+bb', title.lower()))

def find_poker_tables():
    """Busca todas las ventanas de mesas de poker activas"""
    tables = []
    
    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if win32gui.IsWindowVisible(hwnd) and is_poker_table(title):
            tables.append((hwnd, title))
    
    win32gui.EnumWindows(callback, None)
    
    # Ordenar por título para consistencia
    tables.sort(key=lambda x: x[1])
    
    return tables

def get_window_under_cursor():
    """Obtiene el handle de la ventana bajo el cursor"""
    try:
        # Obtener posición actual del cursor
        x, y = pyautogui.position()
        
        # Obtener ventana en esa posición
        hwnd = win32gui.WindowFromPoint((x, y))
        
        # Verificar si es una mesa de poker
        if hwnd:
            title = win32gui.GetWindowText(hwnd)
            if is_poker_table(title):
                return hwnd, title
            
            # Verificar ventana padre
            parent_hwnd = win32gui.GetParent(hwnd)
            if parent_hwnd:
                parent_title = win32gui.GetWindowText(parent_hwnd)
                if is_poker_table(parent_title):
                    return parent_hwnd, parent_title
        
        return None, None
    except Exception as e:
        print(f"Error al detectar ventana bajo cursor: {e}")
        return None, None

def click_on_window_point(hwnd, x_offset, y_offset):
    """Realiza un clic silencioso en una posición relativa de la ventana"""
    try:
        # Enviar mensaje de clic sin mover el cursor físico
        win32api.SendMessage(
            hwnd, 
            win32con.WM_LBUTTONDOWN, 
            win32con.MK_LBUTTON, 
            win32api.MAKELONG(x_offset, y_offset)
        )
        time.sleep(0.05)
        win32api.SendMessage(
            hwnd, 
            win32con.WM_LBUTTONUP, 
            0, 
            win32api.MAKELONG(x_offset, y_offset)
        )
        return True
    except Exception as e:
        print(f"Error al hacer clic: {e}")
        return False

def focus_window(hwnd):
    """Pone el foco en una ventana"""
    try:
        # Guardar ventana actual para poder volver
        current_hwnd = win32gui.GetForegroundWindow()
        
        # Activar ventana objetivo
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)  # Pequeña pausa para asegurar actualización
        
        return hwnd, current_hwnd
    except Exception as e:
        print(f"Error al cambiar foco de ventana: {e}")
        return None, None