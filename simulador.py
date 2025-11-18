from flask import Flask, jsonify
import time
import random

app = Flask(__name__)

# Aviões iniciais (sobre Portugal)
aeronaves = [
    {"hex": "4CA2A1", "flight": "TAP123", "lat": 38.77, "lon": -9.13, "alt_baro": 35000, "gs": 450, "track": 0},
    {"hex": "3421AA", "flight": "RYR555", "lat": 41.24, "lon": -8.68, "alt_baro": 12000, "gs": 300, "track": 180},
    {"hex": "A423BB", "flight": "EJU999", "lat": 37.01, "lon": -7.93, "alt_baro": 28000, "gs": 420, "track": 90},
]

@app.route('/data/aircraft.json')
def mock_aircraft_json():
    # Simular movimento: altera ligeiramente a posição de cada avião
    for aviao in aeronaves:
        aviao['lat'] += random.uniform(-0.05, 0.05)
        aviao['lon'] += random.uniform(-0.05, 0.05)
        aviao['alt_baro'] += random.randint(-100, 100)

    return jsonify({
        "now": time.time(),
        "aircraft": aeronaves
    })

if __name__ == '__main__':
    print("--- SIMULADOR DE RADAR ATIVO ---")
    print("A servir dados em: http://localhost:8080/data/aircraft.json")
    # Corre na porta 8080 para não conflituar com a Web App (porta 5000)
    app.run(host='0.0.0.0', port=8080)