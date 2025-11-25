import sqlite3
import folium
from flask import Flask, render_template_string

DB_NAME = "radar_data.sqlite"
app = Flask(__name__)

def obter_aeronaves():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Busca o timestamp mais recente
    cursor.execute("SELECT MAX(timestamp_recolha) FROM aeronaves")
    res = cursor.fetchone()
    if not res or not res[0]: return []
    timestamp = res[0]
    
    query = """
    SELECT * FROM aeronaves 
    WHERE timestamp_recolha = ? 
    AND lat BETWEEN 40.8 AND 41.8 
    AND lon BETWEEN -9.5 AND -8.0
    """
    cursor.execute(query, (timestamp,))
    return cursor.fetchall()

@app.route('/')
def mapa():
    aeronaves = obter_aeronaves()
    
    # Centrado no Aeroporto Francisco Sá Carneiro (OPO)
    start_coords = [41.248, -8.681]
    m = folium.Map(location=start_coords, zoom_start=10) # Zoom ajustado para a zona
    
    qtd = 0
    for aviao in aeronaves:
        # Lógica de ícones: Preto se no chão, Azul se a voar
        cor = 'blue'
        icone = 'plane'
        
        # Se altitude for < 50 pés, consideramos no chão
        if aviao['altitude'] < 50:
            cor = 'black'
            txt_alt = "NO SOLO (Ground)"
        else:
            txt_alt = f"{aviao['altitude']} ft"

        info = f"""
        <div style="font-family: sans-serif; min-width: 150px;">
            <h4 style="margin: 0 0 5px 0;">{aviao['flight']}</h4>
            <b>Hex:</b> {aviao['hex']}<br>
            <b>Alt:</b> {txt_alt}<br>
            <b>Vel:</b> {aviao['velocidade']} kts
        </div>
        """
        
        folium.Marker(
            [aviao['lat'], aviao['lon']],
            popup=info,
            tooltip=f"{aviao['flight']}",
            icon=folium.Icon(color=cor, icon=icone, prefix='fa')
        ).add_to(m)
        qtd += 1
        
    # HTML Completo com REFRESH AUTOMÁTICO (10 segundos)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Radar Porto - Em Tempo Real</title>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="10"> <!-- ATUALIZA A CADA 10 SEGUNDOS -->
        <style>
            body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
            .header {{ 
                position: absolute; top: 10px; right: 10px; z-index: 999; 
                background: white; padding: 10px; border-radius: 5px; 
                box-shadow: 0 0 5px rgba(0,0,0,0.3);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h3>✈️ Radar Porto</h3>
            <p><b>{qtd}</b> aviões na zona.</p>
            <small>Atualiza a cada 10s</small>
        </div>
        {m._repr_html_()}
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    # '0.0.0.0' permite acesso externo ao contentor
    print("App a correr em http://SEU_IP:5000")
    app.run(host='0.0.0.0', port=5000)