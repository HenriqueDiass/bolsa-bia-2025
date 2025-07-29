# shared/map_components/__init__.py

"""
Map Components Package.

This package exposes a set of professional, reusable functions for plotting
map layers, making them easily accessible for any map generator.
"""

# Importa as funções do módulo 'core' para o nível do pacote 'map_components'
# Isso permite fazer "from shared.map_components import create_base_map"
from .core import (
    create_base_map,
    plot_states_layer,
    plot_highlight_layer,
    plot_polygons_layer,
    plot_choropleth_layer
)