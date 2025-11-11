import sqlite3
import requests
import time
import os
#oooooooo
# --- CONFIGURAÇÃO ---
# MUITO IMPORTANTE: Altere este URL para o endereço IP e porta
# onde o seu dump1090 está a fornecer o ficheiro aircraft.json.
# Se o dump1090 estiver a correr no mesmo contentor, pode ser 'http://127.0.0.1/dump1090/data/aircraft.json'
# ou 'http://127.0.0.1:8080/Sdata/aircraft.json'.
# O caminho '/data/aircraft.json' é o standard nas versões mais recentes.
URL_DUMP1090 = "http://SEU_IP_AQUI/dump1090/data/aircraft.json"

# Nome do ficheiro da base de dados.
# Será criado no mesmo diretório onde o script for executado.
DB_NAME = "radar_data.sqlite"

# Intervalo entre recolhas (em segundos)
INTERVALO_RECOLHA = 60
# --------------------


def setup_database():
    """
    Cria a base de dados e a tabela 'aeronaves' se ainda não existirem.
    """
    print(f"A configurar a base de dados: {DB_NAME}")
    conn = None
    try:
        # Conecta-se (e cria) a base de dados
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Cria a tabela.
        # Guardamos a informação principal de cada "snapshot" de dados.
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS aeronaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_fetch REAL NOT NULL,   -- O 'agora' do ficheiro JSON
            hex TEXT NOT NULL,               -- ICAO hex code (ex: "4ca2ae")
            flight TEXT,                     -- Indicativo de voo (ex: "RYR896L")
            lat REAL,                        -- Latitude
            lon REAL,                        -- Longitude
            altitude INTEGER,                -- Altitude (em pés)
            ground_speed REAL,               -- Velocidade (em nós)
            track REAL                       -- Rumo (em graus)
        );
        ''')

        # Cria um índice para acelerar pesquisas por timestamp (útil na Fase 2)
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp ON aeronaves (timestamp_fetch);
        ''')
        
        conn.commit()
        print("Base de dados configurada com sucesso.")

    except sqlite3.Error as e:
        print(f"Erro ao configurar a base de dados: {e}")
    finally:
        if conn:
            conn.close()


def fetch_data():
    """
    Vai buscar os dados JSON do URL do dump1090.
    Retorna o JSON descodificado ou None em caso de erro.
    """
    try:
        print(f"A contactar: {URL_DUMP1090}")
        response = requests.get(URL_DUMP1090, timeout=10)
        
        # Verifica se o pedido foi bem sucedido
        if response.status_code == 200:
            print("Dados recebidos com sucesso.")
            return response.json()
        else:
            print(f"Erro ao aceder ao URL. Status Code: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erro de rede ou timeout: {e}")
        return None


def save_data(db_conn, data):
    """
    Processa o JSON e guarda os dados de cada aeronave na base de dados.
    """
    try:
        timestamp_now = data.get('now')
        aircraft_list = data.get('aircraft', [])
        
        if not timestamp_now or not aircraft_list:
            print("Formato JSON inesperado. Faltam 'now' ou 'aircraft'.")
            return

        cursor = db_conn.cursor()
        
        aeronaves_guardadas = 0
        
        for ac in aircraft_list:
            # Apenas guardamos aeronaves com dados de posição
            if 'lat' in ac and 'lon' in ac:
                params = (
                    timestamp_now,
                    ac.get('hex'),
                    ac.get('flight', '').strip(), # .strip() para limpar espaços
                    ac.get('lat'),
                    ac.get('lon'),
                    ac.get('alt_baro'), # alt_baro = altitude barométrica
                    ac.get('gs'),       # gs = ground speed
                    ac.get('track')     # track = rumo
                )
                
                sql = """
                INSERT INTO aeronaves 
                (timestamp_fetch, hex, flight, lat, lon, altitude, ground_speed, track)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql, params)
                aeronaves_guardadas += 1
        
        db_conn.commit()
        print(f"Guardadas {aeronaves_guardadas} aeronaves (com posição) de um total de {len(aircraft_list)}.")

    except Exception as e:
        print(f"Erro ao guardar dados: {e}")
        db_conn.rollback() # Desfaz alterações em caso de erro


def main():
    """
    Função principal. Configura a BD e entra num loop infinito
    para recolher e guardar dados.
    """
    # Garante que a BD e a tabela existem antes de começar
    setup_database()
    
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        print("Coletor iniciado. Pressione CTRL+C para parar.")
        
        while True:
            dados = fetch_data()
            
            if dados:
                save_data(conn, dados)
            
            print(f"A aguardar {INTERVALO_RECOLHA} segundos para a próxima recolha...")
            time.sleep(INTERVALO_RECOLHA)
            
    except KeyboardInterrupt:
        print("\nCTRL+C detectado. A encerrar o coletor...")
    except Exception as e:
        print(f"Ocorreu um erro inesperado no loop principal: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão à base de dados fechada.")


if __name__ == "__main__":
    main()