from openai import OpenAI

def analyze_stats(data, api_key, nick="Jugador"):
    """Analiza estadísticas de poker usando GPT"""
    client = OpenAI(api_key=api_key)
    
    try:
        # Calcular gap VPIP-PFR
        gap = float(data['vpip']) - float(data['pfr'])
        
        # Determinar etiqueta de gap
        if gap < 4:
            gap_label = "mínimo (estilo TAG)"
        elif gap < 8:
            gap_label = "moderado"
        elif gap < 12:
            gap_label = "notable (muchos calls)"
        else:
            gap_label = "extremo (muy pasivo)"
        
        # Nombre del jugador para el informe
        nombre_jugador = data.get('player_name', nick)
        
        # Prompt para GPT
        prompt = create_analysis_prompt(nombre_jugador, gap_label, data)
        
        # Realizar petición a GPT
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.7
                )
                
                # Extraer respuesta
                full_response = response.choices[0].message.content.strip()
                
                # Limpiar respuesta
                if "📊 Stats" in full_response:
                    analysis = full_response.split("📊 Stats")[0].strip()
                else:
                    analysis = full_response
                
                return analysis
                
            except Exception as e:
                if attempt == 2:  # Último intento
                    raise
                time.sleep(2)  # Esperar antes de reintentar
        
    except Exception as e:
        return f"⚠️ Error al analizar: {str(e)[:50]}..."

def create_analysis_prompt(nombre_jugador, gap_label, data):
    """Crea el prompt para análisis con GPT"""
    return f"""Eres un jugador profesional de cash online (NL50–NL100). Vas a analizar estadísticas de un oponente y generar un informe **corto, claro y accionable**, como si fuera una nota para otro reg en Discord.

🎯 Estilo directo, sin relleno, sin explicaciones teóricas. Evita tecnicismos largos. Usa lenguaje real de poker: "LAG", "se frena en turn", "flotar flop", "3B light", "spots CO vs BTN", etc.

📌 Evalúa stats **en conjunto**, no por separado. Ejemplos:
- VPIP alto + PFR bajo = pasivo.
- C-Bet flop alta + Turn baja = agresión inconsistente.
- WTSD alto + WSD bajo = paga mucho, gana poco.
- Fold al 3-Bet solo es leak si es >65% o <35%, o no cuadra con su estilo.

📌 Gap VPIP–PFR detectado: {gap_label}

📌 Si tiene menos de 1000 manos, di que el sample es bajo y que los reads son preliminares.

❌ No incluyas ninguna lista de estadísticas numéricas al final ni pongas "Stats clave". Solo el análisis.

---

📄 FORMATO EXACTO DEL INFORME:

🎯 Informe sobre {nombre_jugador}:

1️⃣ Estilo de juego: 
[Estilo en 1–2 líneas, con términos comunes entre regs]

2️⃣ Errores explotables:
- [Leak 1 corto]
- [Leak 2 corto]
- [Leak 3 corto]

3️⃣ Cómo explotarlo:
[Ajustes concisos, estilo "3Btea más en BTN", "flota flop seco", etc.]

---

📊 Stats disponibles:
- Manos: {data['total_manos']}
- BB/100: {data['bb_100']}
- Ganancias USD: {data['win_usd']}
- VPIP: {data['vpip']}%
- PFR: {data['pfr']}%
- 3-Bet: {data['three_bet']}%
- Fold to 3-Bet: {data['fold_to_3bet_pct']}%
- 4-Bet: {data.get('four_bet_preflop_pct', '0')}%
- Fold to 4-Bet: {data.get('fold_to_4bet_pct', '0')}%
- C-Bet Flop: {data['cbet_flop']}%
- C-Bet Turn: {data['cbet_turn']}%
- WWSF: {data['wwsf']}%
- WTSD: {data['wtsd']}%
- WSD: {data['wsd']}%
- Limp Preflop: {data.get('limp_pct', '0')}%
- Limp-Raise: {data.get('limp_raise_pct', '0')}%
- Fold to Flop C-Bet: {data['fold_to_flop_cbet_pct']}%
- Fold to Turn C-Bet: {data['fold_to_turn_cbet_pct']}%
- Probe Bet Turn: {data.get('probe_bet_turn_pct', '0')}%
- Fold to River Bet: {data.get('fold_to_river_bet_pct', '0')}%
- Bet River: {data.get('bet_river_pct', '0')}%
- Overbet Turn: {data.get('overbet_turn_pct', '0')}%
- Overbet River: {data.get('overbet_river_pct', '0')}%
- WSDwBR: {data.get('wsdwbr_pct', '0')}%
"""