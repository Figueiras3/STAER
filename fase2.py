import sqlite3
import folium
from flask import Flask, request, render_template_string

# --- CONFIGURAÇÃO ---
DB_NAME = "radar_data.sqlite"
app = Flask(__name__) # Inicia a aplicação web Flask

# --- LÓGICA DA APLICAÇÃO ---

def obter_dados_atuais(alt_minima=0):
    """
    Vai à base de dados buscar o "snapshot" MAIS RECENTE das aeronaves
    que correspondem ao filtro de altitude.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        # Permite aceder aos resultados por nome de coluna (ex: dados['hex'])
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        # 1. Encontrar o timestamp mais recente
        cursor.execute("SELECT MAX(timestamp_recolha) FROM aeronaves")
        timestamp_recente = cursor.fetchone()[0]
        
        if not timestamp_recente:
            return [], None # Base de dados vazia
            
        # 2. Buscar todas as aeronaves desse timestamp que cumprem o filtro
        query = """
        SELECT * FROM aeronaves 
        WHERE timestamp_recolha = ? AND altitude >= ?
        """
        cursor.execute(query, (timestamp_recente, alt_minima))
        aeronaves = cursor.fetchall()
        
        return aeronaves, timestamp_recente
        
    except sqlite3.Error as e:
        print(f"Erro de base de dados: {e}")
        return [], None
    finally:
        if conn:
            conn.close()

def criar_mapa(lista_aeronaves):
    """
    Cria um objeto de mapa Folium e adiciona os marcadores das aeronaves.
    """
    # Centrar o mapa em Portugal Continental (pode ajustar)
    mapa = folium.Map(location=[39.5, -8.0], zoom_start=7)
    
    if not lista_aeronaves:
        return mapa
        
    for ac in lista_aeronaves:
        # Informação para o popup
        popup_html = f"""
        <b>Voo:</b> {ac['flight']}<br>
        <b>Hex:</b> {ac['hex']}<br>
        <b>Altitude:</b> {ac['altitude']} pés<br>
        <b>Velocidade:</b> {ac['velocidade']} nós
        """
        
        folium.Marker(
            location=[ac['lat'], ac['lon']],
            popup=popup_html,
            tooltip=ac['flight'] or ac['hex'], # Mostra o voo ao passar o rato
            icon=folium.Icon(icon='plane', prefix='fa', color='blue')
        ).add_to(mapa)
        
    return mapa

# --- PÁGINA WEB (A ROTA) ---

@app.route('/', methods=['GET'])
def pagina_mapa():
    """
    Esta é a função que é executada quando alguém acede ao site.
    """
    # Obter o valor do filtro do URL (ex: ?alt_minima=10000)
    # Se não for fornecido, o valor por defeito é 0
    alt_minima = request.args.get('alt_minima', 0, type=int)
    
    # 1. Buscar dados
    aeronaves, timestamp = obter_dados_atuais(alt_minima)
    
    # 2. Criar mapa
    mapa_folium = criar_mapa(aeronaves)
    
    # 3. Converter mapa para HTML
    mapa_html = mapa_folium._repr_html_()
    
    # 4. Criar a página HTML completa (com o formulário de filtro)
    
    html_completo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SWAR - Mapa Radar</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- CSS para o formulário e layout -->
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ display: flex; flex-direction: column; height: 100vh; }}
            .header {{
                background: #f4f4f4;
                padding: 10px 20px;
                border-bottom: 1px solid #ddd;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                z-index: 1000;
            }}
            .header h1 {{ margin: 0; font-size: 1.5em; }}
            .header form {{ margin-top: 10px; }}
            .header label {{ font-weight: bold; margin-right: 10px; }}
            .header input[type="number"] {{ width: 100px; padding: 5px; }}
            .header input[type="submit"] {{ padding: 5px 10px; cursor: pointer; }}
            .info {{ padding: 0 20px 10px; }}
            .map-container {{
                flex-grow: 1; /* Ocupa o resto do espaço */
                height: 100%;
                width: 100%;
            }}
            /* Ajusta o mapa Folium para ocupar o container */
            .folium-map {{ width: 100%; height: 100%; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Visualizador Radar SWAR</h1>
                <!-- Formulário para o filtro de altitude -->
                <form method="GET" action="/">
                    <label for="alt_minima">Altitude Mínima (pés):</label>
                    <input type="number" id="alt_minima" name="alt_minima" value="{alt_minima}">
                    <input type="submit" value="Filtrar">
                </form>
                <div class="info">
                    <p>
                        A mostrar {len(aeronaves)} aeronaves. 
                        Última atualização: {timestamp or 'N/A'}
                    </p>
                </div>
            </div>
            
            <!-- O mapa é injetado aqui -->
            <div class="map-container">
                {mapa_html}
            </div>
        </div>
    </body>
    </html>
    """
    
    # Retorna o HTML completo para o browser
    return render_template_string(html_completo)

# --- EXECUTAR O SERVIDOR ---

if __name__ == '__main__':
    # O host='0.0.0.0' é CRUCIAL para ser acessível 
    # fora do contentor Proxmox (na sua rede local)
    print("Servidor web a iniciar em http://SEU_IP_AQUI:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)