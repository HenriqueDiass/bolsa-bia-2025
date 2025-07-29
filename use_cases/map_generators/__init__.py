# use_cases/map_generators/__init__.py
"""
Expõe todos os geradores de mapa disponíveis para o resto da aplicação.

Este arquivo atua como a API pública do pacote map_generators, permitindo
que outras partes do sistema (como run_use_case.py) importem as funções
necessárias de um único e conveniente local.
"""

from .generate_highlight_map import execute as gerar_mapa_destaque
from .generate_zoom_map import execute as gerar_mapa_zoom
from .generate_states_choropleth import execute as gerar_mapa_estados_coropleth
from .generate_municipalities_choropleth import execute as gerar_mapa_municipios_coropleth
from .generate_state_regional_map import execute as gerar_mapa_regional_estado

# --- ADIÇÃO NOVA ---
# Importa e expõe o nosso novo arquiteto flexível
from .generate_clipped_regions_map import execute as gerar_mapa_regioes_recortadas

__all__ = [
    'gerar_mapa_destaque',
    'gerar_mapa_zoom',
    'gerar_mapa_estados_coropleth',
    'gerar_mapa_municipios_coropleth',
    'gerar_mapa_regional_estado',
    'gerar_mapa_regioes_recortadas', 
]