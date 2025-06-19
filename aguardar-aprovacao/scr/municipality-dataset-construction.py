import requests  # Utilizada para fazer requisições HTTP para APIs web.
import io  # Módulo para trabalhar com fluxos de dados em memória; especificamente, io.UnsupportedOperation é capturado em um 'except'.
import pandas as pd  # Biblioteca fundamental para manipulação e análise de dados em formato tabular (DataFrames).
import time  # Fornece funções para controle de tempo, usada para pausar a execução e evitar sobrecarga de APIs.
import json  # Permite codificar e decodificar dados usando o formato JSON.

# geopaandas foi importado no código original, mas não é usado nas funções atuais.
# Se for usar dados geoespaciais mais tarde, ele será útil.
# import geopandas as gpd 


def obter_municipios_por_sigla_estado(sigla_unidade_federativa: str):
    # Monta a URL da API do IBGE para listar municípios de um estado, convertendo a sigla para maiúsculas.
    url_api_municipios = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{sigla_unidade_federativa.upper()}/municipios"
    # Informa ao usuário qual estado está sendo processado para buscar municípios.
    print(f"Buscando lista de municípios para {sigla_unidade_federativa.upper()} na API de Localidades do IBGE...")

    try:
        resposta_requisicao_municipios = requests.get(url_api_municipios, timeout=30)
        # Lança uma exceção HTTPError se o código de status da resposta indicar um erro (4xx ou 5xx).
        resposta_requisicao_municipios.raise_for_status()
        # Converte o corpo da resposta JSON para um objeto Python (geralmente uma lista de dicionários).
        dados_json_municipios = resposta_requisicao_municipios.json()

        # Verifica se a lista de dados de municípios retornada pela API está vazia.
        if not dados_json_municipios:
            # Exibe um aviso se nenhum município for encontrado para a sigla do estado fornecida.
            print(f"-> AVISO: Nenhum município encontrado para a sigla {sigla_unidade_federativa}.")
            # Retorna None para indicar que nenhum dado foi obtido.
            return None

        # Cria um DataFrame do pandas a partir da lista de dicionários.
        # Seleciona apenas as colunas 'id' (código IBGE) e 'nome' do município.
        dataframe_municipios_do_estado = pd.DataFrame(dados_json_municipios)[['id', 'nome']]

        # Converte a coluna 'id' para o tipo string, o que é útil para consistência e uso em URLs.
        dataframe_municipios_do_estado['id'] = dataframe_municipios_do_estado['id'].astype(str)
        # Informa o sucesso da busca e a quantidade de municípios encontrados.

        print(f"-> Sucesso! {len(dataframe_municipios_do_estado)} municípios encontrados.")
    
        return dataframe_municipios_do_estado

    except requests.exceptions.RequestException as erro_requisicao_municipios:
        # Captura qualquer exceção que ocorra durante a requisição HTTP (problemas de rede, timeout, erros HTTP).
        # Exibe uma mensagem de erro detalhada sobre a falha.
        print(f"-> ERRO ao buscar lista de municípios: {erro_requisicao_municipios}")
        # Retorna None em caso de qualquer falha na requisição.
        return None


def obter_malha_geografica_municipio(codigo_ibge_municipio: str):
    
    # Monta a URL da API de Malhas do IBGE, incluindo o código do município e especificando o formato GeoJSON.
    url_api_malha_municipio = f"https://servicodados.ibge.gov.br/api/v2/malhas/{codigo_ibge_municipio}?formato=application/vnd.geo+json"

    try:
        resposta_requisicao_malha = requests.get(url_api_malha_municipio, timeout=15)
        # Verifica se o código de status da resposta é 404 (Not Found), o que indica que a malha não existe para o ID.
        if resposta_requisicao_malha.status_code == 404:
            # Retorna None se a malha do município não for encontrada na API.
            return None
        # Lança uma exceção HTTPError para outros códigos de status que indicam erro (4xx ou 5xx).
        resposta_requisicao_malha.raise_for_status()
        # Converte o corpo da resposta JSON (que é um GeoJSON) para um objeto Python (dicionário).
        return resposta_requisicao_malha.json()
    except (requests.exceptions.RequestException, io.UnsupportedOperation) as erro_obter_malha:
        # Captura qualquer exceção de requisição (rede, timeout, HTTPError) ou
        # uma exceção específica do módulo io que pode ocorrer em certas operações.
        # Retorna None em caso de qualquer um desses erros.
        return None




def coletar_e_salvar_malhas_municipais(sigla_estado_alvo: str, limite_municipios: int = None):
   
    # 1. Obter a lista de municípios para o estado alvo.
    # Chama a função para buscar os municípios do estado especificado.
    dataframe_municipios_do_estado = obter_municipios_por_sigla_estado(sigla_estado_alvo)

    # Verifica se a lista de municípios foi obtida com sucesso.
    if dataframe_municipios_do_estado is None:
        # Se não houver municípios (erro na API ou estado sem municípios), exibe mensagem e encerra a função.
        print(f"Não foi possível obter a lista de municípios para {sigla_estado_alvo}. Encerrando.")
        return # Encerra a execução da função principal

    # Define o DataFrame de municípios a serem processados.
    # Se 'limite_municipios' for None, 'dataframe_municipios_a_processar' será o DataFrame completo,
    # garantindo que todos os municípios do estado sejam incluídos.
    if limite_municipios is not None:
        dataframe_municipios_a_processar = dataframe_municipios_do_estado.head(limite_municipios)
    else:
        dataframe_municipios_a_processar = dataframe_municipios_do_estado


    # Inicializa listas para armazenar os resultados.
    lista_malhas_municipais_sucesso = []  # Armazena as malhas GeoJSON dos municípios encontrados com sucesso.
    lista_municipios_com_falha = []      # Armazena informações dos municípios cuja malha não foi encontrada.

    # Exibe uma mensagem para o usuário indicando o início da verificação.
    print("\n--- Iniciando a verificação da malha de cada município na API de Malhas do IBGE ---")
    
    # Itera sobre cada linha (município) no DataFrame de municípios a serem processados.
    # `iterrows()` retorna o índice da linha (ignoramos com `_`) e os dados do município como uma Série.
    for indice_linha, dados_municipio_atual in dataframe_municipios_a_processar.iterrows(): #SELECAO DE ITENS QUE EU DESEJO, EU CRIO UMA NOVA TABELA DO COM ELES E DEPOIS EU LEIO ELA 
        codigo_ibge_do_municipio = dados_municipio_atual['id']
        nome_do_municipio = dados_municipio_atual['nome']

        # Exibe o progresso, informando qual município está sendo verificado. 'end=""' mantém o cursor na mesma linha.
        print(f"Verificando malha de {nome_do_municipio} ({codigo_ibge_do_municipio})...", end="")

        # Tenta obter a malha geográfica do município usando sua função específica.
        resultado_malha_geojson = obter_malha_geografica_municipio(codigo_ibge_do_municipio)

        # Verifica se a malha geográfica foi obtida com sucesso (não é None).
        if resultado_malha_geojson is not None:
            # Confere se o GeoJSON contém a estrutura esperada de 'features' e se não está vazio.
            if 'features' in resultado_malha_geojson and resultado_malha_geojson['features']:
                # Adiciona o nome do município à propriedade 'name' dentro do primeiro 'feature' do GeoJSON.
                # Isso enriquece os dados GeoJSON com uma identificação legível.
                resultado_malha_geojson["features"][0]["properties"]["name"] = nome_do_municipio
                # Adiciona o primeiro 'feature' (que contém a geometria e as propriedades) à lista de sucesso.
                lista_malhas_municipais_sucesso.append(resultado_malha_geojson["features"][0])
                # Exibe " OK!" na mesma linha de progresso, indicando sucesso.
                print(" OK!")
            else:
                # Caso o GeoJSON esteja vazio ou sem 'features' válidas, registra como falha.
                print(" FALHOU (GeoJSON vazio ou sem features)")
                # Adiciona o município à lista de falhas com seu nome e código.
                lista_municipios_com_falha.append({'nome_municipio': nome_do_municipio, 'codigo_ibge': codigo_ibge_do_municipio})
        else:
            # Se a função 'obter_malha_geografica_municipio' retornou None, indica falha na obtenção da malha.
            print(" FALHOU!")
            # Adiciona o município à lista de falhas com seu nome e código.
            lista_municipios_com_falha.append({'nome_municipio': nome_do_municipio, 'codigo_ibge': codigo_ibge_do_municipio})

        # Pausa por um curto período para não sobrecarregar a API do IBGE, evitando bloqueios ou erros.
        time.sleep(0.1) 

    # Imprime uma linha separadora para o relatório final.
    print("\n" + "="*50)
    # Imprime o cabeçalho do relatório.
    print("--- RELATÓRIO FINAL DA VERIFICAÇÃO ---")
    # Exibe o total de municípios que foram considerados para verificação.
    print(f"Total de municípios considerados para verificação: {len(dataframe_municipios_a_processar)}")
    # Exibe a quantidade de municípios cujas malhas foram obtidas com sucesso.
    print(f"Municípios com malha geográfica obtida com sucesso: {len(lista_malhas_municipais_sucesso)}")
    # Exibe a quantidade de municípios que apresentaram falha na obtenção da malha.
    print(f"Municípios com dados FALTANTES na API de Malhas: {len(lista_municipios_com_falha)}")

    # 3. Salvar resultados em arquivo JSON.
    # Abre um arquivo JSON no modo de escrita ('w'), com codificação UTF-8 para suportar caracteres especiais.
    # O nome do arquivo segue a convenção kebab-case.
    with open("malhas-municipais-PE.json", "w", encoding="utf-8") as arquivo_saida_json:
        # Salva a lista de GeoJSONs dos municípios com sucesso no arquivo.
        # 'ensure_ascii=False' permite que caracteres não-ASCII sejam gravados diretamente.
        # 'indent=2' formata o JSON com indentação de 2 espaços para melhor legibilidade.
        json.dump(lista_malhas_municipais_sucesso, arquivo_saida_json, ensure_ascii=False, indent=2)
    # Informa o usuário que o arquivo JSON foi salvo.
    print(f"Arquivo JSON salvo como 'malhas-municipais-PE.json'")

    # Se houver municípios que falharam na obtenção da malha, imprime uma lista detalhada.
    if lista_municipios_com_falha:
        print("\nLista de municípios que FALHARAM ao obter a malha:")
        # Itera sobre cada município na lista de falhas.
        for dados_municipio_falho in lista_municipios_com_falha:
            # Imprime o nome e o código IBGE do município que falhou.
            print(f"   - {dados_municipio_falho['nome_municipio']} (Código: {dados_municipio_falho['codigo_ibge']})")





# --- Bloco Principal de Execução ---
# Este bloco é executado apenas quando o script é rodado diretamente (não quando é importado como um módulo).
if __name__ == "__main__":
    # Define a sigla do estado para o qual você deseja coletar os dados.
    # Para o estado de Pernambuco, por exemplo, use "PE".
    SIGLA_ESTADO_PROCESSAR = "PE" 
    
    # Define um limite para o número de municípios a serem processados.
    # ATENÇÃO: Para processar TODOS os municípios do estado, DEIXE ESTA VARIÁVEL COMO NONE.
    # Se você quiser testar com poucos municípios, pode definir um número, ex: 10, 50, etc.
    LIMITE_PARA_TESTE = None 

    # Chama a função principal que orquestra a coleta e salvamento dos dados.
    # Passa a sigla do estado alvo e o limite de municípios (que é None, para processar todos).
    coletar_e_salvar_malhas_municipais(SIGLA_ESTADO_PROCESSAR, LIMITE_PARA_TESTE)