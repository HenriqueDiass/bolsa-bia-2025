# -*- coding: utf-8 -*-
#
# Script final para gerar o mapa do município de Surubim, PE,
# utilizando o código IBGE correto e o método de API mais eficiente.
#

import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import io

# --- Configuração do Município ---
NOME_MUNICIPIO = "Surubim"
# O código correto de 7 dígitos que descobrimos em nossa investigação
CODIGO_IBGE = "2614501"

# URL otimizada que busca apenas a malha de um único município
url = f"https://servicodados.ibge.gov.br/api/v2/malhas/{CODIGO_IBGE}?formato=application/vnd.geo+json"

print(f"Buscando a malha geográfica de '{NOME_MUNICIPIO}' (código: {CODIGO_IBGE})...")
print(f"URL da API: {url}")

try:
    # 1. Fazer a requisição à API do IBGE
    # Um timeout de 20 segundos é mais que suficiente para esta requisição leve
    response = requests.get(url, timeout=20)
    
    # Lança um erro se a resposta for um erro de HTTP (ex: 500 Erro de Servidor)
    # A verificação de 404 (Não Encontrado) é feita implicitamente, pois um erro será lançado.
    response.raise_for_status()

    print("-> Sucesso! Malha geográfica baixada.")

    # 2. Ler os dados geográficos com o GeoPandas
    # io.StringIO trata o texto da resposta como se fosse um arquivo em memória
    gdf = gpd.read_file(io.StringIO(response.text))

    print("-> Gerando o mapa...")

    # 3. Criar a figura e os eixos para o mapa
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # 4. Plotar o GeoDataFrame no eixo criado
    gdf.plot(ax=ax, color='#0077b6', edgecolor='black') # Usando um tom de azul

    # 5. Customizar o gráfico para melhor visualização
    ax.set_title(f"Malha Geográfica do Município de {NOME_MUNICIPIO}", fontsize=16)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Garante que a proporção do mapa não seja distorcida
    plt.gca().set_aspect('equal', adjustable='box') 
    
    # 6. Exibir o mapa em uma nova janela
    plt.show()

except requests.exceptions.HTTPError as errh:
    print(f"\nERRO de HTTP: Não foi possível obter os dados da API.")
    print(f"Código de status: {errh.response.status_code}. Isso pode significar que o código do município está incorreto ou que o servidor do IBGE está com problemas.")
except requests.exceptions.Timeout:
    print("\nERRO de REDE: A requisição demorou demais para responder (Timeout).")
    print("O servidor do IBGE pode estar lento ou sua conexão instável. Tente novamente mais tarde.")
except requests.exceptions.RequestException as err:
    print(f"\nERRO de REDE: Uma falha ocorreu na comunicação com a API: {err}")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")