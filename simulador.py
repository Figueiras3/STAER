from flask import Flask, jsonify
import time
import random
import threading

app = Flask(__name__)

# --- CONFIGURAÇÃO DO TRÁFEGO ---
# Gerar mais aviões para encher o mapa do Porto
aeronaves = [
    # NO CHÃO (Aeroporto OPO)
    {"hex": "4CA2A1", "flight": "TAP123", "lat": 41.238, "lon": -8.670, "alt_baro": "ground", "gs": 15, "track": 350},
    {"hex": "4CA2B2", "flight": "TAP456", "lat": 41.239, "lon": -8.671, "alt_baro": "ground", "gs": 0, "track": 120},
    {"hex": "3421AA", "flight": "RYR101", "lat": 41.240, "lon": -8.672, "alt_baro": "ground", "gs": 5, "track": 200},

    # A DESCOLAR / ATERRAR (Baixa Altitude)
    {"hex": "3421AB", "flight": "RYR555", "lat": 41.250, "lon": -8.680, "alt_baro": 1200, "gs": 160, "track": 340},
    {"hex": "A423BB", "flight": "EJU999", "lat": 41.200, "lon": -8.650, "alt_baro": 2500, "gs": 180, "track": 340},
    {"hex": "A423CC", "flight": "EJU888", "lat": 41.280, "lon": -8.700, "alt_baro": 3000, "gs": 200, "track": 160},

    # EM ESPERA / CIRCULAÇÃO (Média Altitude)
    {"hex": "400001", "flight": "TRA111", "lat": 41.350, "lon": -8.500, "alt_baro": 6000, "gs": 220, "track": 270},
    {"hex": "400002", "flight": "TRA222", "lat": 41.100, "lon": -8.800, "alt_baro": 5500, "gs": 230, "track": 90},

    # CRUZAMENTO (Grande Altitude - Rota Atlântica)
    {"hex": "3C6612", "flight": "DLH111", "lat": 41.150, "lon": -8.550, "alt_baro": 35000, "gs": 450, "track": 190},
    {"hex": "3C6613", "flight": "AFR222", "lat": 41.400, "lon": -8.900, "alt_baro": 38000, "gs": 480, "track": 180},
    {"hex": "3C6614", "flight": "BAW333", "lat": 41.050, "lon": -9.200, "alt_baro": 36000, "gs": 460, "track": 10},
    {"hex": "3C6615", "flight": "IBE444", "lat": 41.300, "lon": -8.200, "alt_baro": 34000, "gs": 440, "track": 200},
]

def mover_avioes():
    """Simula movimento constante"""
    while True:
        for aviao in aeronaves:
            # Movimento baseado no 'track' (simplificado) seria ideal, 
            # mas aleatório funciona bem para teste.
            aviao['lat'] += random.uniform(-0.01, 0.01)
            aviao['lon'] += random.uniform(-0.01, 0.01)
            
            # Varia altitude se não for "ground"
            if isinstance(aviao['alt_baro'], (int, float)):
                aviao['alt_baro'] += random.randint(-50, 50)

        time.sleep(2)

@app.route('/data/aircraft.json')
def mock_aircraft_json():
    # Traduzir campos para o formato que o coletor espera
    # O dump1090-fa usa 'altitude' (pode ser "ground") e 'speed'
    dados_formatados = []
    for a in aeronaves:
        # Criar cópia para não estragar o original
        aviao_export = a.copy()
        # O simulador interno usa 'alt_baro' e 'gs', vamos garantir que sai como 'altitude' e 'speed'
        aviao_export['altitude'] = a.get('alt_baro')
        aviao_export['speed'] = a.get('gs')
        dados_formatados.append(aviao_export)

    return jsonify({
        "now": time.time(),
        "aircraft": dados_formatados
    })

if __name__ == '__main__':
    t = threading.Thread(target=mover_avioes)
    t.daemon = True
    t.start()
    print("--- SIMULADOR TRÁFEGO INTENSO (PORTO) ---")
    app.run(host='0.0.0.0', port=8080)