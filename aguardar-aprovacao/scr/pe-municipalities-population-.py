import requests
import time

# Cabeçalho para simular um navegador (mantemos como boa prática)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Inicializa o contador para a população total de Pernambuco
populacao_total_pe = 0
sigla_uf = "PE" # ### MUDANÇA: Definimos a UF que queremos consultar ###

print(f"Buscando e somando a população de cada município de {sigla_uf}...\n")

try:
    # ### MUDANÇA: URL para buscar os MUNICÍPIOS de Pernambuco ###
    url_municipios = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{sigla_uf}/municipios"
    
    resposta_municipios = requests.get(url_municipios, headers=headers)
    resposta_municipios.raise_for_status()
    municipios = resposta_municipios.json()

    print(f"Encontrados {len(municipios)} municípios em {sigla_uf}.\n")

    # 2. Iterar sobre cada município encontrado
    for municipio in sorted(municipios, key=lambda m: m['nome']):
        municipio_id = municipio['id']
        nome_municipio = municipio['nome']
        
        # ### MUDANÇA PRINCIPAL: Ajuste na URL de consulta ###
        # Usamos localidades=N6 para especificar o nível "Município"
        url_populacao_municipio = (
            f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324"
            f"?localidades=N6[{municipio_id}]" 
        )

        try:
            resposta_populacao = requests.get(url_populacao_municipio, headers=headers)
            resposta_populacao.raise_for_status()
            dados_populacao = resposta_populacao.json()

            # O caminho para extrair o dado continua o mesmo
            if dados_populacao:
                populacao_municipio_str = dados_populacao[0]['resultados'][0]['series'][0]['serie']['2021']
                populacao_municipio = int(populacao_municipio_str)
                
                print(f"- População de {nome_municipio}: {populacao_municipio:,}")

                # 3. Soma ao contador total de Pernambuco
                populacao_total_pe += populacao_municipio
            else:
                print(f"Não foram encontrados dados de população para {nome_municipio}.")

            # Pausa para não sobrecarregar a API (importante para muitos municípios)
            time.sleep(0.1) # Reduzimos um pouco a pausa, mas a mantemos

        except (requests.exceptions.RequestException, IndexError, KeyError) as e:
            print(f"Erro ao processar o município {nome_municipio}: {e}")

    print("\n--------------------------------------------------")
    print(f"POPULAÇÃO TOTAL DE PERNAMBUCO (SOMA DOS MUNICÍPIOS): {populacao_total_pe:,}")
    print("--------------------------------------------------")

except requests.exceptions.RequestException as e:
    print(f"Ocorreu um erro crítico ao buscar a lista de municípios: {e}")