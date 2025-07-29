# use_cases/map_generators/generate_municipalities_choropleth.py

"""
Use case orchestrator for generating a choropleth map of a state's municipalities.

This script is responsible for:
1. Preparing geographic data (loading states and municipalities, clipping).
2. Orchestrating the plotting of the base map and the choropleth layer
   by calling the reusable components from the shared library.
3. Applying a zoom to the state's bounds.
4. Finalizing and saving the map artifact.
"""

import os
import geopandas as gpd
import matplotlib.pyplot as plt

# Imports from our new, clean, and professional component library
from shared.map_components import (
    create_base_map,
    plot_states_layer,
    plot_choropleth_layer
)

def execute(uf: str, coluna: str, caminhos: dict) -> None:
    """
    Generates and saves a choropleth map for a state's municipalities.

    Args:
        uf (str): The abbreviation of the state (e.g., "SP").
        coluna (str): The name of the data column to use for coloring.
        caminhos (dict): A dictionary containing all necessary file paths.
    """
    print(f"\n--- Use Case: GENERATING MUNICIPALITY CHOROPLETH MAP FOR {uf} ---")
    
    projecao: str = "epsg:3857"

    # --- STAGE 1: DATA PREPARATION ---
    print("  -> Preparing geographic data...")
    
    # Load states data once, it will be used for masking and zooming.
    gdf_estados = gpd.read_file(caminhos['estados']).to_crs(projecao)
    mascara_estado = gdf_estados[gdf_estados['abbreviation'] == uf.upper()].copy()
    if mascara_estado.empty:
        print(f"  -> ERROR: State '{uf}' not found. Aborting.")
        return
    mascara_estado['geometry'] = mascara_estado.geometry.buffer(0)

    # Load and clip the municipalities data for the selected state.
    print(f"  -> Loading and clipping municipalities for {uf}...")
    try:
        gdf_municipios = gpd.read_file(caminhos['municipios']).to_crs(projecao)
        gdf_municipios['geometry'] = gdf_municipios.geometry.buffer(0)
        municipios_do_estado = gpd.clip(gdf_municipios, mascara_estado)
        if municipios_do_estado.empty:
            print("  -> WARNING: No municipalities found after clipping.")
            return
    except Exception as e:
        print(f"  -> ERROR: Failed to load or process municipality file. Error: {e}")
        return

    # --- STAGE 2: MAP ORCHESTRATION ---
    print("\n  -> Orchestrating map layer plotting...")
    
    # Stacking order plan
    Z_BASE_ESTADOS = 2
    Z_COROPLETH = 3

    # 2.1. Create the base map: ocean and South America
    fig, ax = create_base_map(caminhos['sulamerica'])
    
    # 2.2. Plot all Brazilian states with a neutral color as a background
    plot_states_layer(ax, gdf_estados, zorder=Z_BASE_ESTADOS)
    
    # 2.3. Plot the rich choropleth layer on top
    # The component handles data validation, coloring, and the legend internally.
    plot_choropleth_layer(ax, municipios_do_estado, data_column=coluna, zorder=Z_COROPLETH)

    # --- STAGE 3: FINALIZATION & ZOOM ---
    print("  -> Finalizing map (zoom, title, and saving)...")
    
    # 3.1. Apply zoom to the state's bounds
    minx, miny, maxx, maxy = mascara_estado.total_bounds
    x_buffer = (maxx - minx) * 0.10
    y_buffer = (maxy - miny) * 0.10
    ax.set_xlim(minx - x_buffer, maxx + x_buffer)
    ax.set_ylim(miny - y_buffer, maxy + y_buffer)

    # 3.2. Set final touches and save
    ax.set_title(f"Mapa Coroplético de '{coluna.capitalize()}' para {uf}", fontsize=16, color='black')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    plt.savefig(caminhos['saida'], dpi=300, bbox_inches='tight', pad_inches=0.05)
    print(f"--- Task Complete! Map saved as '{os.path.basename(caminhos['saida'])}' ---")
    plt.close(fig)