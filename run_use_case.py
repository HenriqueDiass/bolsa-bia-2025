import sys
import os

# =============================================================================
# SEÇÃO 1: CONFIGURAÇÃO DE AMBIENTE E CAMINHOS
# =============================================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
SHARED_DIR = os.path.join(PROJECT_ROOT, "shared")
sys.path.insert(0, PROJECT_ROOT)

# =============================================================================
# SEÇÃO 2: IMPORTAÇÕES DOS USE CASES
# =============================================================================
try:
    from use_cases import (
        FetchStatesUseCase, FetchMunicipalitiesUseCase, FetchImmediateRegionsUseCase, FetchIntermediateRegionsUseCase,
    )
    from use_cases.map_generators import (
        gerar_mapa_destaque, 
        gerar_mapa_zoom,
        gerar_mapa_municipios_coropleth,
        gerar_mapa_estados_coropleth,
        gerar_mapa_regional_estado
    )
    # <--- NOVO: Importa a nova função genérica com um alias claro
    from use_cases.map_generators.generate_clipped_regions_map import execute as gerar_mapa_regioes_recortadas

except ImportError as e:
    print(f"ERRO DE IMPORTAÇÃO: {e}\nVerifique se todas as pastas e arquivos '__init__.py' estão corretos.")
    sys.exit(1)

try:
    import matplotlib.pyplot as plt
    import pandas as pd
    import geopandas as gpd
    MAPS_AVAILABLE = True
except ImportError:
    MAPS_AVAILABLE = False
    print("\nAVISO: Bibliotecas de mapa (matplotlib, pandas, geopandas) não encontradas. Funções de mapa desativadas.")

# =============================================================================
# SEÇÃO 3: CONTROLADORES DE TAREFAS
# =============================================================================

# --- Controladores de Fetch (sem alterações) ---
def run_states():
    print("\n--- Tarefa: DADOS COMPLETOS POR ESTADO ---")
    output_filename = os.path.join(OUTPUT_DIR, "1-complete-data-states.geojson")
    if os.path.exists(output_filename):
        if input(f"   -> Arquivo já existe. Baixar novamente? (s/n): ").lower() != 's':
            print("     Download pulado."); return
    uc = FetchStatesUseCase()
    uc.execute(output_filename=output_filename)
    print("--- Tarefa Concluída! ---")

def run_municipalities():
    uf = input("   -> Digite a Sigla do Estado (ex: PE, SP, RJ): ").upper()
    if not uf or len(uf) != 2: print("   -> Sigla inválida."); return
    print(f"\n--- Tarefa: MUNICÍPIOS DE {uf} ---")
    output_filename = os.path.join(OUTPUT_DIR, f"2-complete-data-municipalities-{uf.lower()}.geojson")
    if os.path.exists(output_filename):
        if input(f"   -> Arquivo já existe. Baixar novamente? (s/n): ").lower() != 's':
            print("     Download pulado."); return
    uc = FetchMunicipalitiesUseCase()
    uc.execute(state_abbreviation=uf, output_filename=output_filename)
    print("--- Tarefa Concluída! ---")

def run_immediate_regions():
    print("\n--- Tarefa: REGIÕES IMEDIATAS DO BRASIL ---")
    output_filename = os.path.join(OUTPUT_DIR, "3-immediate-regions.geojson")
    if os.path.exists(output_filename):
        if input(f"   -> Arquivo já existe. Baixar novamente? (s/n): ").lower() != 's':
            print("     Download pulado."); return
    uc = FetchImmediateRegionsUseCase()
    uc.execute(output_filename=output_filename)
    print("--- Tarefa Concluída! ---")

def run_intermediate_regions():
    print("\n--- Tarefa: REGIÕES INTERMEDIÁRIAS DO BRASIL ---")
    output_filename = os.path.join(OUTPUT_DIR, "4-intermediate-regions.geojson")
    if os.path.exists(output_filename):
        if input(f"   -> Arquivo já existe. Baixar novamente? (s/n): ").lower() != 's':
            print("     Download pulado."); return
    uc = FetchIntermediateRegionsUseCase()
    uc.execute(output_filename=output_filename)
    print("--- Tarefa Concluída! ---")

# --- Controladores de Mapa (adicionando o novo controlador) ---
def run_map_destaque_controller():
    if not MAPS_AVAILABLE: print("Funcionalidade de mapas indisponível."); return
    uf = input("   -> Sigla do Estado para destacar (ex: PE): ").upper()
    if not uf or len(uf) != 2: print("   -> Sigla inválida."); return
    caminhos = {'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"), 'estados': os.path.join(OUTPUT_DIR, "1-complete-data-states.geojson"), 'saida': os.path.join(OUTPUT_DIR, f"mapa_destaque_{uf.lower()}.png")}
    if not os.path.exists(caminhos['estados']): print("\nAVISO: Arquivo de estados não encontrado. Execute a Opção 1."); return
    gerar_mapa_destaque(uf, caminhos)

def run_map_zoom_controller():
    if not MAPS_AVAILABLE: print("Funcionalidade de mapas indisponível."); return
    uf = input("   -> Sigla do Estado para mapa com zoom (ex: PE): ").upper()
    if not uf or len(uf) != 2: print("   -> Sigla inválida."); return
    caminhos = {'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"), 'estados': os.path.join(OUTPUT_DIR, "1-complete-data-states.geojson"), 'municipios': os.path.join(OUTPUT_DIR, f"2-complete-data-municipalities-{uf.lower()}.geojson"), 'saida': os.path.join(OUTPUT_DIR, f"mapa_zoom_municipios_{uf.lower()}.png")}
    if not os.path.exists(caminhos['estados']): print("\nAVISO: Arquivo de estados não encontrado (Opção 1)."); return
    if not os.path.exists(caminhos['municipios']): print(f"\nAVISO: Arquivo de municípios para {uf} não encontrado (Opção 2)."); return
    gerar_mapa_zoom(uf, caminhos)

def run_all_maps_for_state_controller():
    if not MAPS_AVAILABLE: print("Funcionalidade de mapas indisponível."); return
    uf = input("   -> Digite a Sigla do Estado para o relatório completo (ex: PE): ").upper()
    if not uf or len(uf) != 2: print("   -> Sigla inválida."); return
    coluna = input(f"   -> Qual coluna usar para o mapa coroplético de {uf}? (ex: population): ").lower()
    if not coluna: print("   -> Nome da coluna não pode ser vazio."); return
    print(f"\n--- Iniciando Relatório Completo de Mapas para {uf} ---")
    caminho_estados = os.path.join(OUTPUT_DIR, "1-complete-data-states.geojson")
    caminho_municipios = os.path.join(OUTPUT_DIR, f"2-complete-data-municipalities-{uf.lower()}.geojson")
    if not os.path.exists(caminho_estados) or not os.path.exists(caminho_municipios):
        print("\nAVISO: Arquivos de dados necessários não encontrados. Execute as Opções 1 e 2."); return
    gerar_mapa_destaque(uf, {'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"), 'estados': caminho_estados, 'saida': os.path.join(OUTPUT_DIR, f"mapa_destaque_{uf.lower()}.png")})
    gerar_mapa_zoom(uf, {'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"), 'estados': caminho_estados, 'municipios': caminho_municipios, 'saida': os.path.join(OUTPUT_DIR, f"mapa_zoom_municipios_{uf.lower()}.png")})
    gerar_mapa_municipios_coropleth(uf, coluna, {'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"), 'estados': caminho_estados, 'municipios': caminho_municipios, 'saida': os.path.join(OUTPUT_DIR, f"mapa_coropleth_municipios_{uf.lower()}_{coluna}.png")})
    print(f"\n🎉 Relatório completo para {uf} finalizado! 3 mapas foram salvos em 'output'. 🎉")

def run_municipalities_choropleth_controller():
    if not MAPS_AVAILABLE: print("Funcionalidade de mapas indisponível."); return
    uf = input("   -> Sigla do Estado para o mapa coroplético (ex: PE): ").upper()
    if not uf or len(uf) != 2: print("   -> Sigla inválida."); return
    coluna = input(f"   -> Qual coluna dos municípios de {uf} usar para as cores? (ex: population): ").lower()
    if not coluna: print("   -> Nome da coluna não pode ser vazio."); return
    caminhos = {'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"), 'estados': os.path.join(OUTPUT_DIR, "1-complete-data-states.geojson"), 'municipios': os.path.join(OUTPUT_DIR, f"2-complete-data-municipalities-{uf.lower()}.geojson"), 'saida': os.path.join(OUTPUT_DIR, f"mapa_coropleth_municipios_{uf.lower()}_{coluna}.png")}
    if not os.path.exists(caminhos['estados']): print("\nAVISO: Arquivo de estados não encontrado (Opção 1)."); return
    if not os.path.exists(caminhos['municipios']): print(f"\nAVISO: Arquivo de municípios para {uf} não encontrado (Opção 2)."); return
    gerar_mapa_municipios_coropleth(uf, coluna, caminhos)

def run_states_choropleth_controller():
    if not MAPS_AVAILABLE: print("Funcionalidade de mapas indisponível."); return
    coluna = input("   -> Qual coluna do arquivo de estados usar para as cores? (ex: population): ").lower()
    if not coluna: print("   -> Nome da coluna não pode ser vazio."); return
    caminhos = {'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"), 'estados': os.path.join(OUTPUT_DIR, "1-complete-data-states.geojson"), 'saida': os.path.join(OUTPUT_DIR, f"mapa_coropleth_estados_{coluna}.png")}
    if not os.path.exists(caminhos['estados']): print("\nAVISO: Arquivo de estados não encontrado (Opção 1)."); return
    gerar_mapa_estados_coropleth(coluna, caminhos)

def run_state_regional_map_controller():
    if not MAPS_AVAILABLE: print("Funcionalidade de mapas indisponível."); return
    uf = input("   -> Digite a Sigla do Estado para ver suas divisões (ex: PE): ").upper()
    if not uf or len(uf) != 2: print("   -> Sigla inválida."); return
    print("\nVerificando arquivos para o mapa de divisões...")
    caminhos = {
        'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"),
        'estados': os.path.join(OUTPUT_DIR, "1-complete-data-states.geojson"),
        'municipios': os.path.join(OUTPUT_DIR, f"2-complete-data-municipalities-{uf.lower()}.geojson"),
        'imediatas': os.path.join(OUTPUT_DIR, "3-immediate-regions.geojson"),
        'intermediarias': os.path.join(OUTPUT_DIR, "4-intermediate-regions.geojson"),
        'saida': os.path.join(OUTPUT_DIR, f"mapa_divisoes_{uf.lower()}.png")
    }
    arquivos_obrigatorios = {'estados': "Opção 1", 'imediatas': "Opção 3", 'intermediarias': "Opção 4"}
    arquivos_faltando = False
    for key, opcao in arquivos_obrigatorios.items():
        if not os.path.exists(caminhos[key]):
            print(f"   -> ERRO: Arquivo obrigatório de '{key}' não foi encontrado.")
            print(f"   -> Por favor, execute a '{opcao}' no menu principal primeiro.")
            arquivos_faltando = True
    if arquivos_faltando: return
    gerar_mapa_regional_estado(uf, caminhos)

# <--- NOVO: Controlador para a nova função de mapa de regiões recortadas
def run_clipped_regions_map_controller():
    if not MAPS_AVAILABLE: print("Funcionalidade de mapas indisponível."); return
    uf = input("   -> Digite a Sigla do Estado para o mapa (ex: PE): ").upper()
    if not uf or len(uf) != 2: print("   -> Sigla inválida."); return

    region_choice = input("   -> Qual tipo de região? (1 para Imediatas, 2 para Intermediárias): ")
    if region_choice == '1':
        region_type = 'imediatas'
        required_file = 'imediatas'
        required_option = 'Opção 3'
    elif region_choice == '2':
        region_type = 'intermediarias'
        required_file = 'intermediarias'
        required_option = 'Opção 4'
    else:
        print("   -> Escolha inválida. Use 1 ou 2."); return
    
    print(f"\nVerificando arquivos para o mapa de Regiões {region_type.capitalize()}...")
    caminhos = {
        'sulamerica': os.path.join(SHARED_DIR, "south_america.geojson"),
        'estados': os.path.join(OUTPUT_DIR, "1-complete-data-states.geojson"),
        'imediatas': os.path.join(OUTPUT_DIR, "3-immediate-regions.geojson"),
        'intermediarias': os.path.join(OUTPUT_DIR, "4-intermediate-regions.geojson"),
        'saida': os.path.join(OUTPUT_DIR, f"mapa_regiao_{region_type}_{uf.lower()}.png")
    }
    
    # Verifica se os arquivos base (estados) e o específico da região existem
    if not os.path.exists(caminhos['estados']):
        print("   -> ERRO: Arquivo de 'estados' não foi encontrado. Execute a 'Opção 1'."); return
    if not os.path.exists(caminhos[required_file]):
        print(f"   -> ERRO: Arquivo de '{required_file}' não foi encontrado. Execute a '{required_option}'."); return

    # Chama a função importada
    gerar_mapa_regioes_recortadas(uf=uf, caminhos=caminhos, region_type=region_type)

# =============================================================================
# SEÇÃO 4: INTERFACE COM O USUÁRIO E LOOP PRINCIPAL
# =============================================================================
def display_menu():
    print("\n+------------------------------------------------------+")
    print("|          PAINEL DE CONTROLE DE DADOS E MAPAS         |")
    print("+------------------------------------------------------+")
    print("| DADOS GEOJSON                                        |")
    print("|  1. Baixar Dados dos Estados                         |")
    print("|  2. Baixar Dados dos Municípios (por Estado)         |")
    print("|  3. Baixar Dados das Regiões Imediatas               |")
    print("|  4. Baixar Dados das Regiões Intermediárias          |")
    print("|  5. EXECUTAR TODOS OS FETCHS em sequência            |")
    if MAPS_AVAILABLE:
        print("+------------------------------------------------------+")
        print("| MAPAS                                                |")
        print("|  6. Gerar Mapa de Destaque (Individual)              |")
        print("|  7. Gerar Mapa com Zoom (Individual)                 |")
        print("|  8. Gerar Relatório Completo para um Estado (3 Mapas)|")
        print("|  9. Gerar Mapa Coroplético de Municípios             |")
        print("| 10. Gerar Mapa Coroplético dos Estados               |")
        print("| 11. Gerar Mapa de Divisões de um Estado              |")
        print("| 12. Gerar Mapa de Regiões Recortadas (Imed./Interm.) |") # <--- NOVO
    print("+------------------------------------------------------+")
    print("|  0. Sair do programa                                 |")
    print("+------------------------------------------------------+")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    while True:
        display_menu()
        choice = input("Digite o número da sua escolha e pressione Enter: ")
        try:
            if choice == '1': run_states()
            elif choice == '2': run_municipalities()
            elif choice == '3': run_immediate_regions()
            elif choice == '4': run_intermediate_regions()
            elif choice == '5':
                print("\n--- ATENÇÃO: Executando todos os fetchs de dados. ---")
                run_states(); run_immediate_regions(); run_intermediate_regions()
                print("\nPara baixar os municípios, execute a opção 2 individualmente.")
                print("\n🎉 TAREFAS DE FETCH CONCLUÍDAS! 🎉")
            elif choice == '6' and MAPS_AVAILABLE: run_map_destaque_controller()
            elif choice == '7' and MAPS_AVAILABLE: run_map_zoom_controller()
            elif choice == '8' and MAPS_AVAILABLE: run_all_maps_for_state_controller()
            elif choice == '9' and MAPS_AVAILABLE: run_municipalities_choropleth_controller()
            elif choice == '10' and MAPS_AVAILABLE: run_states_choropleth_controller()
            elif choice == '11' and MAPS_AVAILABLE: run_state_regional_map_controller()
            # <--- NOVO: Adiciona a chamada ao novo controlador
            elif choice == '12' and MAPS_AVAILABLE: run_clipped_regions_map_controller()
            elif choice == '0':
                print("Saindo do programa. Até logo!"); break
            else:
                print("Opção inválida!")
        except Exception as e:
            print(f"\n❌ Ocorreu um erro inesperado: {e}")
        if choice != '0':
            input("\nPressione Enter para continuar...")