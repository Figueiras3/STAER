import sqlite3
import requests
import time
import datetime


URL_DUMP1090 = "http://localhost:8080/data/aircraft.json"

# Nome da base de dados (será criada na mesma pasta)
DB_NAME = "radar_data.sqlite"

# Intervalo de recolha em segundos
INTERVALO = 10

def criar_tabela():
    """
    Cria a base de dados e a tabela se não existirem.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Criar tabela 'aeronaves'
    # Guardamos também o 'timestamp' para saber QUANDO a aeronave estava naquela posição
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS aeronaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp_recolha DATETIME DEFAULT CURRENT_TIMESTAMP,
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
    print("Base de dados verificada/criada com sucesso.")

def obter_dados():
    """
    Vai buscar o JSON ao dump1090.
    """
    try:
        print(f"A conectar a {URL_DUMP1090}...")
        resposta = requests.get(URL_DUMP1090, timeout=5)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print(f"Erro no pedido: {resposta.status_code}")
            return None
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def guardar_dados(dados_json):
    """
    Recebe o JSON e guarda as aeronaves na BD.
    """
    if not dados_json or 'aircraft' not in dados_json:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    lista_aeronaves = dados_json['aircraft']
    contador = 0

    for aviao in lista_aeronaves:
        # Só guardamos se tiver coordenadas (lat/lon) válidas
        if 'lat' in aviao and 'lon' in aviao:
            hex_code = aviao.get('hex')
            flight = aviao.get('flight', '').strip() # remove espaços extra
            lat = aviao.get('lat')
            lon = aviao.get('lon')
            alt = aviao.get('alt_baro', 0) # altitude barométrica
            gs = aviao.get('gs', 0)        # ground speed
            track = aviao.get('track', 0)  # rumo

            cursor.execute('''
            INSERT INTO aeronaves (hex, flight, lat, lon, altitude, velocidade, track)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (hex_code, flight, lat, lon, alt, gs, track))
            
            contador += 1

    conn.commit()
    conn.close()
    print(f"--> Guardados {contador} registos na base de dados.")

def main():
    """
    Função Principal
    """
    print("--- INICIANDO COLETOR SWAR ---")
    criar_tabela()
    
    while True:
        dados = obter_dados()
        if dados:
            guardar_dados(dados)
        
        print(f"A aguardar {INTERVALO} segundos...")
        time.sleep(INTERVALO)

if __name__ == "__main__":
    main()