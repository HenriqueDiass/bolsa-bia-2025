# use_cases/map_generators/generate_state_regional_map.py

"""
Use case orchestrator for generating a state's regional division map.
This script prepares data and then orchestrates the plotting of map layers
by calling reusable components from the shared library.
"""

import os
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# Imports from our new, clean, and professional component library
from shared.map_components import (
    create_base_map,
    plot_states_layer,
    plot_highlight_layer,
    plot_polygons_layer
)


def execute(uf: str, caminhos: dict) -> None:
    """
    Generates and saves a map showing the regional divisions for a given state.

    Args:
        uf (str): The abbreviation of the state (e.g., "SP").
        caminhos (dict): A dictionary containing all necessary file paths.
    """
    print(f"\n--- Use Case: GENERATING REGIONAL DIVISIONS MAP FOR {uf} ---")
    
    projecao: str = "epsg:3857"

    # --- STAGE 1: DATA PREPARATION ---
    print("  -> Preparing geographic data...")
    gdf_estados = gpd.read_file(caminhos['estados']).to_crs(projecao)
    mascara_estado = gdf_estados[gdf_estados['abbreviation'] == uf.upper()].copy()
    if mascara_estado.empty: 
        print(f"  -> ERROR: State '{uf}' not found. Aborting."); return
    mascara_estado['geometry'] = mascara_estado.geometry.buffer(0)

    municipios_recortados = None
    caminho_municipios = caminhos.get('municipios')
    if caminho_municipios and os.path.exists(caminho_municipios):
        try:
            gdf_municipios = gpd.read_file(caminho_municipios).to_crs(projecao)
            gdf_municipios['geometry'] = gdf_municipios.geometry.buffer(0)
            recorte_tentativa = gpd.clip(gdf_municipios, mascara_estado)
            if not recorte_tentativa.empty:
                municipios_recortados = recorte_tentativa
                print("  -> Municipality data successfully prepared.")
        except Exception as e:
            print(f"  -> WARNING: Failed to process municipality data. Error: {e}")
    else:
        print("  -> Municipality data not found.")

    gdf_imediatas = gpd.read_file(caminhos['imediatas']).to_crs(projecao)
    gdf_imediatas['geometry'] = gdf_imediatas.geometry.buffer(0)
    imediatas_recortadas = gpd.clip(gdf_imediatas, mascara_estado)
    
    gdf_intermediarias = gpd.read_file(caminhos['intermediarias']).to_crs(projecao)
    gdf_intermediarias['geometry'] = gdf_intermediarias.geometry.buffer(0)
    intermediarias_recortadas = gpd.clip(gdf_intermediarias, mascara_estado)

    # --- STAGE 2: MAP ORCHESTRATION WITH EXPLICIT Z-ORDER ---
    print("\n  -> Orchestrating map layer plotting with manual z-order...")

    # Stacking order plan: Lower numbers are at the bottom.
    Z_BASE_PAISES = 1
    Z_BASE_ESTADOS = 2
    Z_DESTAQUE_VERMELHO = 3
    Z_COBERTURA_CINZA = 4   # CRITICAL: Must be higher than the red highlight
    Z_LINHAS_REGIOES = 5
    Z_BORDA_FINAL = 6

    # 2.1. Create the base canvas (already has zorder=1)
    fig, ax = create_base_map(caminhos['sulamerica'])
    
    # 2.2. Plot base layers with explicit z-order
    plot_states_layer(ax, gdf_estados, zorder=Z_BASE_ESTADOS)
    plot_highlight_layer(ax, gdf_estados, uf, zorder=Z_DESTAQUE_VERMELHO)
    
    # 2.3. Plot the COVERAGE layer with a z-order that puts it ON TOP of the red highlight
    if municipios_recortados is not None:
        print("  -> Plotting municipality layer as state background...")
        plot_polygons_layer(ax, municipios_recortados, color='#f5f5f5', edgecolor='#d3d3d3', linewidth=0.3, zorder=Z_COBERTURA_CINZA)
        region_line_color = '#0077b6'
    else:
        print("  -> Plotting neutral state background...")
        mascara_estado.plot(ax=ax, color='#f5f5f5', edgecolor='none', zorder=Z_COBERTURA_CINZA)
        region_line_color = '#696969'

    # 2.4. Plot region lines on top of the gray coverage
    print("  -> Plotting regional division lines...")
    plot_polygons_layer(ax, imediatas_recortadas, facecolor='none', edgecolor=region_line_color, linewidth=1.0, zorder=Z_LINHAS_REGIOES)
    plot_polygons_layer(ax, intermediarias_recortadas, facecolor='none', edgecolor='#d00000', linewidth=1.2, zorder=Z_LINHAS_REGIOES)

    # 2.5. Plot the final state border on top of everything for a clean finish
    mascara_estado.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=0.8, zorder=Z_BORDA_FINAL)
    
    # --- STAGE 3: FINALIZATION ---
    print("  -> Finalizing map (legend, title, and saving)...")
    minx, miny, maxx, maxy = mascara_estado.total_bounds
    ax.set_xlim(minx - (maxx - minx) * 0.05, maxx + (maxx - minx) * 0.05)
    ax.set_ylim(miny - (maxy - miny) * 0.05, maxy + (maxy - miny) * 0.05)

    legenda_intermediaria = mlines.Line2D([], [], color='#d00000', lw=1.8, label='Região Intermediária')
    legenda_imediata = mlines.Line2D([], [], color=region_line_color, lw=1.0, label='Região Imediata')
    ax.legend(handles=[legenda_intermediaria, legenda_imediata], loc='lower right', fontsize='small', facecolor='white', framealpha=0.8)

    ax.set_title(f"Divisões Regionais de {uf}", fontsize=16, color='black')
    
    plt.savefig(caminhos['saida'], dpi=300, bbox_inches='tight', pad_inches=0.05)
    print(f"--- Task Complete! Map saved as '{os.path.basename(caminhos['saida'])}' ---")
    plt.close(fig)