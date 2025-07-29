# use_cases/map_generators/generate_clipped_regions_map.py

"""
Use case orchestrator for generating a map of a specific type of region
clipped to a state's boundaries. This is a flexible, parameterized architect.
"""

import os
import geopandas as gpd
import matplotlib.pyplot as plt

# Importa os componentes reutilizáveis da nossa biblioteca central
# Supondo que você tenha um arquivo 'shared/map_components.py' com essas funções.
# Se não, você precisará adaptar ou incluir essas funções aqui.
from shared.map_components import (
    create_base_map,
    plot_states_layer,
    plot_polygons_layer
)

def execute(uf: str, caminhos: dict, region_type: str) -> None:
    """
    Generates and saves a map showing a specific type of regional division
    for a given Brazilian state.

    Args:
        uf (str): The abbreviation of the state (e.g., "PE").
        caminhos (dict): A dictionary containing all necessary file paths.
        region_type (str): The type of region to plot ('imediatas' or 'intermediarias').
    """
    
    # --- STAGE 0: PARAMETER VALIDATION ---
    print(f"\n--- Use Case: Gerando Mapa de Regiões '{region_type.capitalize()}' para {uf} ---")
    if region_type == 'imediatas':
        caminho_regiao = caminhos['imediatas']
        cor_linha = '#0077b6' # Azul
    elif region_type == 'intermediarias':
        caminho_regiao = caminhos['intermediarias']
        cor_linha = '#d00000' # Vermelho
    else:
        print(f"  -> ERRO: Tipo de região inválido '{region_type}'. Deve ser 'imediatas' ou 'intermediarias'.")
        return

    projecao: str = "epsg:3857"

    # --- STAGE 1: DATA PREPARATION ---
    print("  -> Preparando dados geográficos...")
    try:
        gdf_estados = gpd.read_file(caminhos['estados']).to_crs(projecao)
        mascara_estado = gdf_estados[gdf_estados['abbreviation'] == uf.upper()].copy()
        if mascara_estado.empty: 
            print(f"  -> ERRO: Estado '{uf}' não encontrado. Abortando."); return
        mascara_estado['geometry'] = mascara_estado.geometry.buffer(0)

        gdf_regioes = gpd.read_file(caminho_regiao).to_crs(projecao)
        gdf_regioes['geometry'] = gdf_regioes.geometry.buffer(0)
        
        regioes_recortadas = gpd.clip(gdf_regioes, mascara_estado)
        if regioes_recortadas.empty:
            print("  -> AVISO: Nenhuma região encontrada para este estado após o recorte.")
            # Gerar mesmo assim um mapa vazio para consistência
            # return # Descomente se preferir não gerar o mapa
    except Exception as e:
        print(f"  -> ERRO: Falha durante a preparação dos dados. Erro: {e}")
        return

    # --- STAGE 2: MAP ORCHESTRATION ---
    print("\n  -> Orquestrando a plotagem das camadas do mapa...")

    Z_BASE_ESTADOS = 2
    Z_REGIOES_RECORTADAS = 3
    Z_BORDA_FINAL = 4

    fig, ax = create_base_map(caminhos['sulamerica'])
    plot_states_layer(ax, gdf_estados, zorder=Z_BASE_ESTADOS)
    
    if not regioes_recortadas.empty:
        plot_polygons_layer(ax, regioes_recortadas, facecolor='none', edgecolor=cor_linha, linewidth=1.2, zorder=Z_REGIOES_RECORTADAS)
    
    mascara_estado.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=0.8, zorder=Z_BORDA_FINAL)

    # --- STAGE 3: FINALIZATION & ZOOM ---
    print("  -> Finalizando o mapa...")
    
    minx, miny, maxx, maxy = mascara_estado.total_bounds
    x_buffer, y_buffer = (maxx - minx) * 0.10, (maxy - miny) * 0.10
    ax.set_xlim(minx - x_buffer, maxx + x_buffer)
    ax.set_ylim(miny - y_buffer, maxy + y_buffer)

    ax.set_title(f"Regiões {region_type.capitalize()} de {uf}", fontsize=16, color='black')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # AJUSTE IMPORTANTE: O caminho de saída agora é construído dinamicamente
    # e usa o dicionário 'caminhos' como os outros controladores.
    caminho_saida = caminhos['saida']
    
    plt.savefig(caminho_saida, dpi=300, bbox_inches='tight', pad_inches=0.05)
    print(f"--- Tarefa Concluída! Mapa salvo como '{os.path.basename(caminho_saida)}' ---")
    plt.close(fig)