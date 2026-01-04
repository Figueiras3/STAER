import sqlite3
import requests
import time
from datetime import datetime

URL_DUMP1090 = "https://ads-b.jcboliveira.xyz/dump1090/data/aircraft.json"

DB_NAME = "radar_data.sqlite"
INTERVALO = 10 

def criar_tabela():
    """Cria a tabela na base de dados se não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS aeronaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp_recolha DATETIME,
        hex TEXT,
        flight TEXT,
        lat REAL,
        lon REAL,
        altitude INTEGER,
        velocidade REAL,
        track REAL
    )
    ''')
    conn.commit()
    conn.close()
    print("Base de dados pronta.")

def obter_dados():
    """Faz o pedido HTTP ao site externo."""
    try:
        print(f"A ler dados de {URL_DUMP1090}...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        resposta = requests.get(URL_DUMP1090, headers=headers, timeout=10)
        
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print(f"Erro no pedido: {resposta.status_code}")
            return None
            
    except Exception as e:
        print(f"Erro de conexão: {e}")
    return None

def tratar_altitude(alt_cru):
    """Converte 'ground' para 0 e garante que é número."""
    if alt_cru == "ground":
        return 0
    try:
        return int(alt_cru)
    except:
        return 0

def guardar_dados(dados_json):
    """Guarda os aviões na BD com o mesmo carimbo temporal."""
    if not dados_json or 'aircraft' not in dados_json:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    lista_aeronaves = dados_json['aircraft']
    
    agora = datetime.now() 
    
    contador = 0

    for aviao in lista_aeronaves:
        if 'lat' in aviao and 'lon' in aviao:
            
            hex_code = aviao.get('hex')
            flight = aviao.get('flight', 'N/A').strip() 
            lat = aviao.get('lat')
            lon = aviao.get('lon')
            alt = tratar_altitude(aviao.get('altitude', 0))
            velocidade = aviao.get('speed', 0)
            track = aviao.get('track', 0)

            cursor.execute('''
            INSERT INTO aeronaves (timestamp_recolha, hex, flight, lat, lon, altitude, velocidade, track)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (agora, hex_code, flight, lat, lon, alt, velocidade, track))
            
            contador += 1

    conn.commit()
    conn.close()
    print(f"--> Sincronizado: Guardados {contador} aviões reais às {agora.strftime('%H:%M:%S')}.")

def main():
    print(f"--- COLETOR ONLINE INICIADO ({URL_DUMP1090}) ---")
    criar_tabela()
    while True:
        dados = obter_dados()
        if dados:
            guardar_dados(dados)
        
        time.sleep(INTERVALO)

if __name__ == "__main__":
    main()