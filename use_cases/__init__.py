# use_cases/__init__.py (VERSÃO FINAL E CORRETA)
# Expõe as classes de Use Case de Fetch para o resto da aplicação.

# MUDANÇA: Usamos o caminho completo 'use_cases.fetch_...' em vez de '.fetch_...'
# Isso torna a importação mais robusta quando o script principal é executado da raiz.
from use_cases.fetch_states.index import FetchStatesUseCase
from use_cases.fetch_municipalities.index import FetchMunicipalitiesUseCase
from use_cases.fetch_immediate_regions.index import FetchImmediateRegionsUseCase
from use_cases.fetch_intermediate_regions.index import FetchIntermediateRegionsUseCase

# A lista de "convidados" para este pacote de alto nível.
__all__ = [
    'FetchStatesUseCase',
    'FetchMunicipalitiesUseCase',
    'FetchImmediateRegionsUseCase',
    'FetchIntermediateRegionsUseCase',
]