# use_cases/map_generators/generate_states_choropleth.py

"""
Use case orchestrator for generating a choropleth map of Brazilian states.

This script is responsible for:
1. Preparing the geographic data for the states.
2. Orchestrating the plotting of the base map and the choropleth layer
   by calling the reusable components from the shared library.
3. Finalizing and saving the map artifact.
"""

import os
import geopandas as gpd
import matplotlib.pyplot as plt

# Imports from our new, clean, and professional component library
from shared.map_components import (
    create_base_map,
    plot_choropleth_layer
)

def execute(coluna: str, caminhos: dict) -> None:
    """
    Generates and saves a choropleth map of Brazilian states.

    Args:
        coluna (str): The name of the data column to use for coloring.
        caminhos (dict): A dictionary containing all necessary file paths.
    """
    print(f"\n--- Use Case: GENERATING STATES CHOROPLETH MAP BY '{coluna}' ---")
    
    projecao: str = "epsg:3857"

    # --- STAGE 1: DATA PREPARATION ---
    # The "architect" is responsible for loading the data it will orchestrate.
    print("  -> Preparing geographic data...")
    try:
        gdf_estados = gpd.read_file(caminhos['estados']).to_crs(projecao)
        print("  -> States data successfully prepared.")
    except Exception as e:
        print(f"  -> ERROR: Failed to load states file. Error: {e}")
        return

    # --- STAGE 2: MAP ORCHESTRATION ---
    print("\n  -> Orchestrating map layer plotting...")
    
    # Stacking order plan: The choropleth layer goes on top of the base map.
    Z_COROPLETH = 2

    # 2.1. Create the base map: ocean and South America
    fig, ax = create_base_map(caminhos['sulamerica'])
    
    # 2.2. Plot the rich choropleth layer on top using our powerful component
    # The component handles data validation, coloring, and the legend internally.
    plot_choropleth_layer(
        ax, 
        geodataframe=gdf_estados, 
        data_column=coluna, 
        cmap='plasma', # Using the 'plasma' colormap as in the original script
        zorder=Z_COROPLETH
    )

    # --- STAGE 3: FINALIZATION ---
    print("  -> Finalizing and saving the map...")
    
    ax.set_title(f"Mapa Coroplético dos Estados por '{coluna.capitalize()}'", fontsize=16, color='black')
    
    plt.savefig(caminhos['saida'], dpi=300, bbox_inches='tight', pad_inches=0.05)
    print(f"--- Task Complete! Map saved as '{os.path.basename(caminhos['saida'])}' ---")
    plt.close(fig)