from PIL import Image, ImageFilter, ImageEnhance

def generate_image_hash(img, hash_size=32):
    """Genera un hash perceptual de una imagen para comparación"""
    # Reducir tamaño para comparación
    img = img.resize((hash_size, hash_size//2), Image.LANCZOS)
    
    # Convertir a escala de grises
    img = img.convert("L")
    
    # Obtener datos de píxeles
    pixels = list(img.getdata())
    
    # Calcular valor promedio
    avg = sum(pixels) / len(pixels)
    
    # Generar hash basado en píxeles sobre/bajo promedio
    return "".join('1' if pixel > avg else '0' for pixel in pixels)

def enhance_image_for_ocr(img):
    """Mejora una imagen para mejor reconocimiento OCR"""
    # Aumentar nitidez
    img = img.filter(ImageFilter.SHARPEN)
    
    # Aumentar contraste
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    
    # Aumentar brillo ligeramente
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)
    
    return img

def preprocess_asian_chars(img):
    """Preprocesamiento específico para mejorar la detección de caracteres asiáticos"""
    # Aumentar tamaño
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    
    # Aplicar filtro de nitidez más agresivo
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)
    
    # Aumentar contraste
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    
    return img

def create_test_image(text="Test OCR 测试 テスト"):
    """Crea una imagen de prueba con texto para calibrar OCR"""
    img = Image.new('RGB', (200, 50), color=(0, 0, 0))
    d = ImageDraw.Draw(img)
    
    try:
        # Intentar cargar una fuente que soporte caracteres asiáticos
        from PIL import ImageFont
        try:
            # Fuentes que suelen tener buen soporte para caracteres asiáticos
            font = ImageFont.truetype("NotoSansCJK-Regular.ttc", 20)
        except:
            try:
                font = ImageFont.truetype("Arial Unicode MS", 20)
            except:
                font = None
                
        if font:
            d.text((10, 10), text, font=font, fill=(255, 255, 255))
        else:
            d.text((10, 10), text, fill=(255, 255, 255))
    except:
        # Fallback si hay problemas con fuentes
        d.text((10, 10), text, fill=(255, 255, 255))
    
    return img