import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import xyzservices.providers as xyz
from shapely.geometry import Point
import numpy as np

# === 1. Dados dos hospitais como lista de dicionários ===
hospitais = [
    {'nome': 'Hospital Carpina', 'lat': -7.845, 'lon': -35.251, 'casos': 2},
    {'nome': 'Hospital Surubim A', 'lat': -7.835, 'lon': -35.741, 'casos': 30},
    {'nome': 'Hospital Surubim B', 'lat': -7.825, 'lon': -35.751, 'casos': 20},
    {'nome': 'Hospital Nazaré', 'lat': -7.744, 'lon': -35.229, 'casos': 90},
    {'nome': 'Hospital Lagoa', 'lat': -7.918, 'lon': -35.296, 'casos': 6},
    {'nome': 'Hospital Bom Jardim', 'lat': -7.797, 'lon': -35.583, 'casos': 10}
]

# === 2. Transformar lista em DataFrame e criar GeoDataFrame ===
df_hospitais = pd.DataFrame(hospitais)
geometry = [Point(xy) for xy in zip(df_hospitais['lon'], df_hospitais['lat'])]
gdf_hospitais = gpd.GeoDataFrame(df_hospitais, geometry=geometry, crs="EPSG:4326")

# === 3. Carregar arquivo GeoJSON ===
gdf_municipios = gpd.read_file(r'C:\Users\Carlos Henrique\Documents\pernambuco_municipios.geojson')

# === 4. Criar dados fictícios de casos por município ===
np.random.seed(42)  # Para resultados reproduzíveis
gdf_municipios['casos'] = np.random.randint(10, 500, size=len(gdf_municipios))

# === 5. Plotar o mapa ===
fig, ax = plt.subplots(1, 1, figsize=(12, 12))

# Plotar o coroplético dos municípios
gdf_municipios.plot(column='casos', 
                    cmap='Reds', 
                    linewidth=0.8, 
                    ax=ax, 
                    edgecolor='0.8', 
                    legend=True)

# Reprojetar hospitais para o mesmo CRS dos municípios
gdf_hospitais = gdf_hospitais.to_crs(gdf_municipios.crs)

# Plotar os hospitais
gdf_hospitais.plot(ax=ax, 
                   color='blue', 
                   markersize=gdf_hospitais['casos'], 
                   alpha=0.6, 
                   label='Hospitais')

# ✅ Correção: usar provedor seguro
ctx.add_basemap(ax, source=xyz.OpenStreetMap.Mapnik, crs=gdf_municipios.crs)

# Ajustes finais
plt.title('Mapa de Casos de Doenças e Hospitais - Pernambuco', fontsize=16)
plt.axis('off')
plt.legend(['Hospitais'])

plt.show()