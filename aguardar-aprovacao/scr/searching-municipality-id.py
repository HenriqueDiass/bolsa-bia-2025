# --- SCRIPT DE DESCOBERTA ---
import geopandas as gpd
import requests
import io

# URL para obter as malhas de todos os municípios de Pernambuco
url_municipios_pe = "https://servicodados.ibge.gov.br/api/v2/malhas/26?resolucao=5&formato=application/vnd.geo+json"

print("Tentando baixar e inspecionar os dados dos municípios...")

try:
    # Baixa os dados
    response = requests.get(url_municipios_pe)
    response.raise_for_status()  # Verifica se o download foi bem sucedido

    # Lê os dados com o GeoPandas
    gdf_municipios = gpd.read_file(io.StringIO(response.text))

    print("\n\n--- SUCESSO! OS DADOS FORAM LIDOS. ---")
    print("Abaixo está a estrutura de dados real recebida da API do IBGE.")
    
    # 1. Mostra a lista de nomes de colunas
    print("\n[1] As colunas disponíveis são:")
    print(list(gdf_municipios.columns))
    
    # 2. Mostra as 5 primeiras linhas da tabela para vermos os dados
    print("\n[2] As 5 primeiras linhas de dados são:")
    print(gdf_municipios.head())

except Exception as e:
    print(f"\nOcorreu um erro durante a execução: {e}")