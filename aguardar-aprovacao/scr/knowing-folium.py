import folium
import json
import pandas as pd

# Caminho do arquivo GeoJSON
geojson_file = r'C:\Users\Carlos Henrique\Documents\pernambuco_municipios.geojson'

# Abrir o GeoJSON com codificação UTF-8
with open(geojson_file, encoding='utf-8') as f:
    geojson_data = json.load(f)

# Dados agregados por município
dados = {
    'NM_MUN': ['Carpina', 'Surubim', 'Nazaré da Mata', 'Lagoa de Itaenga', 'Bom Jardim'],
    'casos': [2, 50, 90, 6, 10]
}
df_casos = pd.DataFrame(dados)

# Criar mapa centrado em Pernambuco
m = folium.Map(location=[-8.28, -35.07], zoom_start=8)

# Adicionar o Choropleth
folium.Choropleth(
    geo_data=geojson_data,
    name='choropleth',
    data=df_casos,
    columns=['NM_MUN', 'casos'],
    key_on='feature.properties.NM_MUN',
    fill_color='Blues',
    fill_opacity=0.8,
    line_opacity=0.2,
    legend_name='Casos de Asma',
    nan_fill_color='white',
    threshold_scale=[0, 5, 20, 50, 100]
).add_to(m)

# Exemplo: Localização dos hospitais com casos individuais
hospitais = [
    {'nome': 'Hospital Carpina', 'lat': -7.845, 'lon': -35.251, 'casos': 2},
    {'nome': 'Hospital Surubim A', 'lat': -7.835, 'lon': -35.741, 'casos': 30},
    {'nome': 'Hospital Surubim B', 'lat': -7.825, 'lon': -35.751, 'casos': 20},
    {'nome': 'Hospital Nazaré', 'lat': -7.744, 'lon': -35.229, 'casos': 90},
    {'nome': 'Hospital Lagoa', 'lat': -7.918, 'lon': -35.296, 'casos': 6},
    {'nome': 'Hospital Bom Jardim', 'lat': -7.797, 'lon': -35.583, 'casos': 10}
]

# Adicionar marcadores padrão e CircleMarkers
for hosp in hospitais:
    # Marker tradicional
    folium.Marker(
        location=[hosp['lat'], hosp['lon']],
        popup=f"{hosp['nome']}: {hosp['casos']} casos",
        icon=folium.Icon(color='blue', icon='plus-sign')
    ).add_to(m)
    
    # CircleMarker proporcional aos casos
    folium.CircleMarker(
        location=[hosp['lat'], hosp['lon']],
        radius=max(3, hosp['casos'] / 5),  # Ajuste para não ficar muito pequeno
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"{hosp['nome']}: {hosp['casos']} casos"
    ).add_to(m)

# Adicionar controle de camadas
folium.LayerControl().add_to(m)

# Salvar o mapa
m.save('mapa_casos_asma_com_hospitaisDiversos.html')

print("✅ Mapa salvo como 'mapa_casos_asma_com_hospitaisDi.html'")