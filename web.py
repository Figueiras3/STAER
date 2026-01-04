import sqlite3
import folium
from flask import Flask, render_template_string, request

DB_NAME = "radar_data.sqlite"
app = Flask(__name__)

def obter_aeronaves(filtro_zona=False, apenas_voo=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(timestamp_recolha) FROM aeronaves")
    res = cursor.fetchone()
    if not res or not res[0]: return []
    timestamp = res[0]
    
    query = "SELECT * FROM aeronaves WHERE timestamp_recolha = ?"
    params = [timestamp]

    if filtro_zona:
        query += " AND lat BETWEEN 40.8 AND 41.8 AND lon BETWEEN -9.5 AND -8.0"
    
    if apenas_voo:
        query += " AND altitude > 0"

    cursor.execute(query, params)
    return cursor.fetchall()

@app.route('/')
def mapa():
    zona_porto = request.args.get('zona') == '1'
    apenas_voo = request.args.get('voo') == '1'

    aeronaves = obter_aeronaves(filtro_zona=zona_porto, apenas_voo=apenas_voo)
    
    start_coords = [41.248, -8.681] if zona_porto else [39.5, -8.0]
    zoom = 10 if zona_porto else 7

    m = folium.Map(location=start_coords, zoom_start=zoom)
    
    qtd = 0
    for aviao in aeronaves:
        cor = 'blue'
        icone = 'plane'
        
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
        
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>STAER Radar</title>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="10">
        <style>
            body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
            .control-panel {{ 
                position: absolute; top: 10px; right: 10px; z-index: 999; 
                background: white; padding: 15px; border-radius: 8px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                min-width: 200px;
            }}
            .stat {{ font-size: 1.2em; font-weight: bold; color: #333; }}
            form {{ margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px; }}
            label {{ display: block; margin-bottom: 5px; cursor: pointer; }}
            button {{ 
                margin-top: 10px; width: 100%; padding: 8px; 
                background: #007bff; color: white; border: none; 
                border-radius: 4px; cursor: pointer;
            }}
            button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="control-panel">
            <h3>✈️ Radar STAER</h3>
            <div class="stat">{qtd} aviões visíveis</div>
            <small>Atualizado automaticamente</small>
            
            <form action="/" method="get">
                <b>Filtros:</b><br>
                <label>
                    <input type="checkbox" name="zona" value="1" {'checked' if zona_porto else ''}>
                    Apenas Zona do Porto
                </label>
                <label>
                    <input type="checkbox" name="voo" value="1" {'checked' if apenas_voo else ''}>
                    Esconder aviões no chão
                </label>
                <button type="submit">Aplicar Filtros</button>
            </form>
        </div>
        {m._repr_html_()}
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)