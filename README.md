PokerBot TRACK

📋 Descripción
PokerBot TRACK es una herramienta avanzada de análisis para jugadores de poker que proporciona estadísticas e información estratégica sobre oponentes en tiempo real. Utilizando tecnología OCR (Reconocimiento Óptico de Caracteres) y algoritmos de IA, PokerBot TRACK identifica a los jugadores en las mesas de poker y genera análisis detallados para ayudarte a tomar mejores decisiones durante el juego.
✨ Características Principales

Detección Automática: Reconoce nicks de jugadores directamente desde la mesa de poker en tiempo real
Estadísticas Completas: Muestra métricas clave como VPIP, PFR, 3-Bet, Fold to 3-Bet, WTSD, WSD, C-Bet y más
Análisis Estratégico con IA: Genera análisis de juego personalizados mediante GPT para identificar debilidades y proponer estrategias de contraataque
Múltiples Modos de Operación:

Análisis manual con hotkey (Alt+Q por defecto)
Análisis con clic derecho sobre un jugador
Modo automático que analiza todas las mesas activas periódicamente


Historial de Búsquedas: Almacena análisis previos para consulta rápida
Personalización Completa: Configura qué estadísticas mostrar y su formato
Soporte Multilingüe: Compatible con caracteres asiáticos (chino, japonés, coreano)

🛠️ Instalación
Requisitos

Windows 10/11
Python 3.8 o superior
Cuenta en API de estadísticas de poker
Clave API de OpenAI (para análisis con GPT)

Pasos de Instalación

Clona o descarga este repositorio:
git clone https://github.com/tuusuario/pokerbot-track.git
cd pokerbot-track

Instala las dependencias:
pip install -r requirements.txt

Crea un archivo .env en el directorio raíz con tus claves API:
TOKEN=tu_token_api_de_poker
OPENAI_API_KEY=tu_clave_api_openai

Ejecuta la aplicación:
python main.py


📊 Guía de Uso
Análisis Manual

Inicia la aplicación y asegúrate de que esté en ejecución
Abre tu cliente de poker favorito y accede a una mesa
Utiliza una de las siguientes opciones:

Presiona Alt+Q con el cursor sobre la mesa de poker
Haz clic derecho sobre el nick de un jugador
Busca manualmente un nick en la pestaña "Principal"



Modo Automático

Activa el "Modo Automático" en la pestaña "Principal"
La aplicación buscará y analizará periódicamente todas las mesas de poker abiertas
Los resultados se mostrarán automáticamente en la mesa correspondiente

Configuración
En la pestaña "Configuración" puedes ajustar:

API Keys (token y OpenAI)
Hotkey personalizada
Coordenadas OCR para diferentes clientes de poker
Sala por defecto (XPK, PS, GG, WPN, 888)
Estadísticas a mostrar y su formato
Tema claro/oscuro

Acciones Rápidas

Ver Historial: Consulta análisis previos en la pestaña "Historial"
Copiar Resultados: Copia estadísticas, análisis o ambos al portapapeles
Limpiar Caché: Reinicia la caché de nicks si detectas problemas de reconocimiento

🔧 Calibración OCR
Para mejorar la precisión del reconocimiento de nicks:

Ve a la pestaña "Configuración"
Haz clic en "Calibrar OCR"
Sigue las instrucciones para seleccionar el área donde aparecen los nicks en tu cliente de poker
Las coordenadas se guardarán automáticamente

📊 Estadísticas Disponibles
AbreviaturaSignificadoDescripciónVPIPVoluntarily Put Money In Pot% de veces que el jugador pone dinero voluntariamentePFRPre-Flop Raise% de veces que sube preflop3B3-Bet% de veces que hace 3-Bet preflopF3BFold to 3-Bet% de veces que foldea ante un 3-BetWTSDWent to Showdown% de veces que llega al showdownWSDWon at Showdown% de veces que gana en el showdownCFC-Bet Flop% de veces que hace continuation bet en el flopCTC-Bet Turn% de veces que hace continuation bet en el turnFFCFold to Flop C-Bet% de veces que foldea ante un C-Bet en flopFTCFold to Turn C-Bet% de veces que foldea ante un C-Bet en turn
🧩 Estructura del Proyecto
/
├── main.py                 # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── assets/                 # Recursos gráficos
│   └── icon.ico            # Icono de la aplicación
├── config/                 # Archivos de configuración
│   ├── config.json         # Configuración general
│   └── historial.json      # Historial de búsquedas
├── src/
│   ├── config/             # Gestión de configuración
│   ├── core/               # Funcionalidad principal
│   │   ├── api_client.py   # Cliente de API de estadísticas
│   │   ├── gpt_client.py   # Cliente de API de OpenAI
│   │   ├── ocr_engine.py   # Motor de reconocimiento OCR
│   │   └── poker_analyzer.py # Análisis de datos de poker
│   ├── ui/                 # Interfaz de usuario
│   │   ├── dialogs/        # Diálogos y ventanas emergentes
│   │   ├── tabs/           # Pestañas de la interfaz principal
│   │   └── main_window.py  # Ventana principal
│   └── utils/              # Utilidades y herramientas
🔒 Seguridad
PokerBot TRACK utiliza un archivo .env separado para almacenar claves API sensibles. Por seguridad:

NUNCA compartas tu archivo .env ni tus claves API
No incluyas claves API directamente en el código o en archivos compartidos
Utiliza cuentas y claves de API dedicadas para esta aplicación

💻 Tecnologías Utilizadas

Python: Lenguaje principal de programación
PaddleOCR: Motor de reconocimiento óptico de caracteres
OpenAI GPT: Análisis estratégico avanzado
ttkbootstrap: Interfaz gráfica moderna
Win32API: Interacción con ventanas de Windows

📜 Licencia
Este proyecto está licenciado bajo los términos de la licencia MIT. Ver LICENSE para más detalles.
⚠️ Aviso Legal
Este software está diseñado para uso educativo e informativo únicamente. Asegúrate de cumplir con los términos de servicio de todas las plataformas de poker que utilices. El autor no se hace responsable del uso indebido de esta herramienta.
