import urllib.parse
import requests

def get_player_stats(nick, sala, token, server_url):
    """Obtiene estadísticas del jugador desde la API"""
    try:
        # Codificar el nick para URL
        nick_encoded = urllib.parse.quote(nick, safe='')
        url = f"{server_url}/api/jugador/{sala}/{nick_encoded}"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Realizar petición
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            error_message = f"Error al obtener stats: Código {response.status_code}"
            if response.text:
                error_message += f", {response.text}"
            raise Exception(error_message)
        
        data = response.json()
        return data
    
    except requests.exceptions.Timeout:
        raise Exception("Timeout al conectar con la API. Verifica la conexión.")
    
    except Exception as e:
        # Intento alternativo con fragmento del nick
        if ' ' in nick:
            first_part = nick.split(' ')[0]
            print(f"Intentando con fragmento: '{first_part}'")
            return get_player_stats(first_part, sala, token, server_url)
        raise