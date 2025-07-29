# shared/map_components/core.py
"""
A professional, centralized library of reusable map components.

This module provides a set of high-level functions to plot specific,
stylized layers onto a Matplotlib map, using GeoPandas. Each function
is designed to be a self-contained "Lego block" for map construction.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.axes import Axes

DEFAULT_PROJECTION: str = "epsg:3857"

def create_base_map(south_america_file_path: str) -> tuple[Figure, Axes]:
    """
    Creates the base figure and axes for a map, plotting the South American continent.

    Args:
        south_america_file_path (str): The file path to the South America geo data.

    Returns:
        A tuple containing the Matplotlib Figure and Axes objects (fig, ax).
    """
    ocean_color: str = '#a6c9e2'
    country_fill_color: str = '#e0e0e0'
    country_border_color: str = "#8a8787"
    
    south_america_gdf: gpd.GeoDataFrame = gpd.read_file(south_america_file_path).to_crs(DEFAULT_PROJECTION)
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 12))
    fig.patch.set_facecolor(ocean_color)
    ax.set_facecolor(ocean_color)
    
    south_america_gdf.plot(ax=ax, color=country_fill_color, edgecolor=country_border_color, zorder=1)
    
    ax.set_axis_off()
    return fig, ax

def plot_states_layer(ax: Axes, states_gdf: gpd.GeoDataFrame, zorder: int = 2) -> None:
    """
    Plots the layer of all Brazilian states with a neutral background color.

    Args:
        ax (Axes): The Matplotlib Axes on which to plot.
        states_gdf (gpd.GeoDataFrame): The GeoDataFrame containing all Brazilian states.
        zorder (int, optional): The stacking order for the plot. Defaults to 2.
    """
    fill_color: str = '#f0e6c2'
    border_color: str = "#8a8787"
    states_gdf.plot(ax=ax, color=fill_color, edgecolor=border_color, linewidth=0.7, zorder=zorder)

def plot_highlight_layer(ax: Axes, states_gdf: gpd.GeoDataFrame, state_abbreviation: str, zorder: int = 3) -> None:
    """
    Plots a single state with a strong highlight color (e.g., red).

    Args:
        ax (Axes): The Matplotlib Axes on which to plot.
        states_gdf (gpd.GeoDataFrame): The GeoDataFrame containing all Brazilian states.
        state_abbreviation (str): The abbreviation of the state to highlight (e.g., "SP").
        zorder (int, optional): The stacking order for the plot. Defaults to 3.
    """
    selected_state_gdf: gpd.GeoDataFrame = states_gdf[states_gdf['abbreviation'] == state_abbreviation.upper()].copy()
    
    if not selected_state_gdf.empty:
        selected_state_gdf.plot(ax=ax, color='red', edgecolor='darkred', linewidth=1.5, zorder=zorder)
    else:
        print(f"WARNING: Highlight state '{state_abbreviation}' not found.")

def plot_polygons_layer(ax: Axes, geodataframe: gpd.GeoDataFrame, **kwargs) -> None:
    """
    A flexible and safe function to plot any GeoDataFrame containing polygons.
    It accepts keyword arguments (kwargs) to control the visual style, including zorder.

    Args:
        ax (Axes): The Matplotlib Axes on which to plot.
        geodataframe (gpd.GeoDataFrame): A GeoDataFrame to be plotted.
        **kwargs: Visual styling arguments passed to the .plot() method.
    """
    polygons_gdf: gpd.GeoDataFrame = geodataframe[geodataframe.geometry.type.isin(['Polygon', 'MultiPolygon'])]
    
    if not polygons_gdf.empty:
        polygons_gdf.plot(ax=ax, **kwargs)

# ========================================================================
# ESTA É A FUNÇÃO QUE ESTAVA FALTANDO NO SEU ARQUIVO
# ========================================================================
def plot_choropleth_layer(ax: Axes, geodataframe: gpd.GeoDataFrame, data_column: str, cmap: str = 'viridis', use_log_scale: bool = True, **kwargs) -> bool:
    """
    Plots a professional choropleth layer, coloring polygons based on a data column.
    Includes data validation, cleaning, and a configurable legend.

    Args:
        ax (Axes): The Matplotlib Axes on which to plot.
        geodataframe (gpd.GeoDataFrame): The GeoDataFrame containing the geometry and data.
        data_column (str): The name of the column to use for coloring.
        cmap (str, optional): The name of the colormap to use. Defaults to 'viridis'.
        use_log_scale (bool, optional): Whether to use a logarithmic scale for colors. Defaults to True.
        **kwargs: Other visual styling arguments passed to the .plot() method (e.g., zorder).

    Returns:
        bool: True if the plot was successful, False otherwise.
    """
    if data_column not in geodataframe.columns:
        print(f"ERROR: The data column '{data_column}' was not found in the GeoDataFrame.")
        return False

    valid_data_gdf: gpd.GeoDataFrame = geodataframe[geodataframe[data_column].notna() & (geodataframe[data_column] > 0)].copy()
    
    if valid_data_gdf.empty:
        print(f"WARNING: No valid data found in column '{data_column}' to plot.")
        return False

    norm = None
    if use_log_scale:
        norm = mcolors.LogNorm(vmin=valid_data_gdf[data_column].min(), vmax=valid_data_gdf[data_column].max())
        legend_label = f"{data_column.replace('_', ' ').capitalize()} (Log Scale)"
    else:
        legend_label = data_column.replace('_', ' ').capitalize()

    legend_keywords = {
        'label': legend_label,
        'orientation': "horizontal",
        'shrink': 0.6,
        'pad': 0.02
    }
    
    style = {'cmap': cmap, 'linewidth': 0.5, 'edgecolor': '0.8', 'legend': True, 'legend_kwds': legend_keywords, 'norm': norm}
    style.update(kwargs) # Combina os estilos padrão com quaisquer outros que você passar
    
    valid_data_gdf.plot(column=data_column, ax=ax, **style)
    return True