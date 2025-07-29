# use_cases/map_generators/generate_highlight_map.py

"""
Use case orchestrator for generating a simple state highlight map.

This script is responsible for:
1. Preparing the necessary geographic data (loading the states file).
2. Orchestrating the plotting of the base map, the states layer, and the
   highlight layer by calling the reusable components from the shared library.
3. Finalizing and saving the map artifact.
"""

import os
import geopandas as gpd
import matplotlib.pyplot as plt

# 1. Imports são limpos e vêm da nossa biblioteca de componentes centralizada.
from shared.map_components import (
    create_base_map,
    plot_states_layer,
    plot_highlight_layer
)


def execute(uf: str, caminhos: dict) -> None:
    """
    Generates and saves a map highlighting a specific Brazilian state.

    Args:
        uf (str): The abbreviation of the state to highlight (e.g., "SP").
        caminhos (dict): A dictionary containing all necessary file paths.
    """
    print(f"\n--- Use Case: GENERATING HIGHLIGHT MAP FOR {uf} ---")
    
    projecao: str = "epsg:3857"

    # --- ETAPA 1: PREPARAÇÃO DOS DADOS ---
    # O "arquiteto" agora é responsável por carregar os dados que serão usados.
    print("  -> Preparing geographic data...")
    gdf_estados = gpd.read_file(caminhos['estados']).to_crs(projecao)

    # --- ETAPA 2: ORQUESTRAÇÃO DO DESENHO DO MAPA ---
    print("  -> Orchestrating map layer plotting with manual z-order...")

    # Definindo nosso plano de empilhamento para garantir a ordem correta.
    Z_BASE_ESTADOS = 2
    Z_DESTAQUE_VERMELHO = 3

    # 2. A "caixa-preta" foi substituída por uma sequência explícita de chamadas.
    # Cada passo da construção do mapa agora é claro e legível.
    fig, ax = create_base_map(caminhos['sulamerica'])
    plot_states_layer(ax, gdf_estados, zorder=Z_BASE_ESTADOS)
    plot_highlight_layer(ax, gdf_estados, uf, zorder=Z_DESTAQUE_VERMELHO)
    
    # --- ETAPA 3: FINALIZAÇÃO ---
    print("  -> Finalizing and saving the map...")
    
    # O fundo da figura é azul (definido em create_base_map), então o título branco funciona bem.
    ax.set_title(f'Destaque para o estado de {uf}', fontsize=16, color='white')

    # Salvando o resultado final
    plt.savefig(caminhos['saida'], dpi=300, bbox_inches='tight')
    print(f"--- Task Complete! Map saved as '{os.path.basename(caminhos['saida'])}' ---")
    
    # Fechando a figura para liberar memória
    plt.close(fig)