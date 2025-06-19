import requests
import time

# Cabeçalho para simular um navegador
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Inicializa o contador
populacao_total_brasil = 0

print("Buscando e somando a população de cada estado...\n")

try:
    # 1. Obter a lista de todos os estados (isso continua igual)
    url_estados = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    resposta_estados = requests.get(url_estados, headers=headers)
    resposta_estados.raise_for_status()
    estados = resposta_estados.json()

    # 2. Iterar sobre cada estado
    for estado in sorted(estados, key=lambda e: e['nome']):
        uf_id = estado['id']
        
        # ### NOVO: URL da API de Agregados v3 para Estimativa de População (Agregado 6579) ###
        # Variável 9324 = População estimada
        # Usamos o período mais recente disponível, que pode ser consultado na documentação do agregado.
        # Por agora, vamos usar um período fixo recente e estável, como 2021.
        url_populacao_estado = (
            f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324"
            f"?localidades=N3[{uf_id}]"
        )

        try:
            resposta_populacao = requests.get(url_populacao_estado, headers=headers)
            resposta_populacao.raise_for_status()
            dados_populacao = resposta_populacao.json()

            # ### NOVO: O caminho para extrair o valor da população mudou ###
            # A resposta é uma lista, então pegamos o primeiro item [0]
            # e navegamos pela estrutura do JSON.
            if dados_populacao:
                populacao_estado_str = dados_populacao[0]['resultados'][0]['series'][0]['serie']['2021']
                populacao_estado = int(populacao_estado_str) # Converte o valor de string para inteiro
                
                print(f"- População de {estado['nome']} ({estado['sigla']}): {populacao_estado:,}")

                # 3. Soma ao contador
                populacao_total_brasil += populacao_estado
            else:
                print(f"Não foram encontrados dados de população para {estado['nome']}.")

            # Pausa para não sobrecarregar a API
            time.sleep(0.3)

        except (requests.exceptions.RequestException, IndexError, KeyError) as e:
            # Captura erros de requisição, ou caso a estrutura do JSON seja inesperada
            print(f"Erro ao processar o estado {estado['sigla']}: {e}")

    print("\n--------------------------------------------------")
    print(f"POPULAÇÃO TOTAL DO BRASIL (SOMA DOS ESTADOS): {populacao_total_brasil:,}")
    print("--------------------------------------------------")

except requests.exceptions.RequestException as e:
    print(f"Ocorreu um erro crítico ao buscar a lista de estados: {e}")