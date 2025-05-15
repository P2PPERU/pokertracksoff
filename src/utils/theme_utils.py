import ttkbootstrap as ttk

# Colores del tema poker
POKER_GREEN = "#006622"
POKER_RED = "#8B0000"
POKER_BLUE = "#000066"
POKER_GOLD = "#D4AF37"
POKER_BLACK = "#171717"

def apply_custom_theme(root, theme_name="poker"):
    """Aplica un tema personalizado para PokerBot Pro"""
    
    if theme_name == "poker":
        # Define el tema personalizado de Poker
        ttk.Style().theme_use("darkly")
        
        # Personalizar colores de botones
        ttk.Style().configure("success.TButton", background=POKER_GREEN)
        ttk.Style().configure("danger.TButton", background=POKER_RED)
        ttk.Style().configure("primary.TButton", background=POKER_BLUE)
        ttk.Style().configure("warning.TButton", background=POKER_GOLD)
        ttk.Style().configure("secondary.TButton", background=POKER_BLACK)
        
        # Personalizar notebooks
        ttk.Style().configure("TNotebook", background=POKER_BLACK)
        ttk.Style().configure("TNotebook.Tab", background=POKER_BLACK, foreground="white")
        ttk.Style().map("TNotebook.Tab", background=[("selected", POKER_GREEN)])
        
        # Personalizar frames de tarjetas
        ttk.Style().configure("light.TFrame", background="#212121")
        
        # Personalizar etiquetas
        ttk.Style().configure("primary.TLabel", foreground=POKER_GREEN)