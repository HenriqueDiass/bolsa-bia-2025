import requests
import json
import time
import pandas as pd

def obter_lista_estados_brasileiros():
    # Define a URL da API do IBGE para listar os estados.
    url_api_estados = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    
    try:
        resposta_requisicao_estados = requests.get(url_api_estados, timeout=30)
        resposta_requisicao_estados.raise_for_status()
        # Converte a resposta JSON da API em um objeto Python (lista de dicionários).
        dados_json_estados = resposta_requisicao_estados.json()
        
        # Cria um DataFrame do pandas a partir dos dados JSON.
        # Seleciona apenas as colunas 'id', 'sigla' e 'nome'.
        dataframe_estados = pd.DataFrame(dados_json_estados)[['id', 'sigla', 'nome']]
        # Converte a coluna 'id' para o tipo string, garantindo consistência.
        dataframe_estados['id'] = dataframe_estados['id'].astype(str)
        
        # Retorna o DataFrame com os dados dos estados.
        return dataframe_estados
        
    except requests.exceptions.RequestException as erro_requisicao_estados:
        # Captura qualquer exceção que ocorra durante a requisição (ex: problemas de conexão, timeout).
        # Exibe uma mensagem de erro detalhada.
        print(f"Erro ao buscar estados: {erro_requisicao_estados}")
        # Retorna None, indicando que a operação falhou.
        return None

def obter_regioes_imediatas_por_estado(id_identificador_estado: str):
    # Define a URL da API do IBGE para listar as regiões imediatas de um estado específico.
    
    url_api_regioes_imediatas = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{id_identificador_estado}/regioes-imediatas"
    
    try:
    
        resposta_requisicao_regioes = requests.get(url_api_regioes_imediatas, timeout=30)
        # Levanta uma exceção HTTPError para códigos de status de erro.
        resposta_requisicao_regioes.raise_for_status()
        # Converte a resposta JSON da API em um objeto Python (lista de dicionários).  PARA MANIPULAR OS DADOS DA MELHOR FORMA
        dados_json_regioes = resposta_requisicao_regioes.json()
        
        # Verifica se a lista de regiões imediatas retornada está vazia.
        if not dados_json_regioes:
            # Exibe uma mensagem informativa se nenhuma região imediata for encontrada.
            print(f"-> Nenhuma região imediata encontrada para o estado ID {id_identificador_estado}.")
            # Retorna None, indicando que não há dados.
            return None
            
        # Cria um DataFrame do pandas a partir dos dados JSON.
        # Seleciona apenas as colunas 'id' e 'nome'.
        dataframe_regioes_imediatas = pd.DataFrame(dados_json_regioes)[['id', 'nome']]
        # Converte a coluna 'id' para o tipo string, garantindo consistência.
        dataframe_regioes_imediatas['id'] = dataframe_regioes_imediatas['id'].astype(str)  #ASTYPE -- CONVERSAO
        
        # Retorna o DataFrame com os dados das regiões imediatas.
        return dataframe_regioes_imediatas
        
    except requests.exceptions.RequestException as erro_requisicao_regioes:
        # Captura qualquer exceção que ocorra durante a requisição.
        # Exibe uma mensagem de erro detalhada.
        print(f"Erro ao buscar regiões imediatas para estado ID {id_identificador_estado}: {erro_requisicao_regioes}")
        # Retorna None em caso de falha.
        return None

def obter_metadados_malha_regiao_imediata(id_identificador_regiao_imediata: str):
   
    # Define a URL da API do IBGE para obter metadados da malha de uma região imediata.
    url_api_metadados_malha = f"https://servicodados.ibge.gov.br/api/v4/malhas/regioes-imediatas/{id_identificador_regiao_imediata}/metadados"
    
    try:
        # Realiza uma requisição GET para a URL da API.
        # O 'timeout' define o tempo máximo de espera pela resposta em segundos.
        resposta_requisicao_metadados = requests.get(url_api_metadados_malha, timeout=15)
        
        # Verifica se o código de status da resposta é 404 (Não Encontrado).
        if resposta_requisicao_metadados.status_code == 404:
            # Retorna None se a região imediata não for encontrada na API de Malhas.
            return None
        
        resposta_requisicao_metadados.raise_for_status()
        
        # Converte a resposta JSON da API em um objeto Python (dicionário).
        # Retorna os metadados da malha.
        return resposta_requisicao_metadados.json()
        
    except requests.exceptions.RequestException:
        # Captura qualquer exceção que ocorra durante a requisição.
        # Retorna None em caso de falha.
        return None

def coletar_e_salvar_dados_regioes_imediatas():
    
    # Obter a lista completa de estados brasileiros.
    dataframe_todos_estados = obter_lista_estados_brasileiros()
    
    # Verifica se a lista de estados foi obtida com sucesso.
    if dataframe_todos_estados is None:
        # Exibe uma mensagem de erro e encerra o programa se a lista de estados não puder ser obtida.
        print("Erro ao obter lista de estados. Encerrando o processamento.")
        

    # Inicializa listas para armazenar os resultados de sucesso e falha.
    lista_regioes_com_sucesso = []
    lista_regioes_com_falha = []

    # Exibe uma mensagem inicial para o usuário.
    print("Iniciando a coleta de regiões imediatas e metadados de malhas...\n")

    # Itera sobre cada linha (estado) no DataFrame de estados.
    
    for indice_linha, dados_estado_atual in dataframe_todos_estados.iterrows():
        # Exibe qual estado está sendo processado no momento.
        print(f"Processando estado {dados_estado_atual['sigla']} - {dados_estado_atual['nome']} (ID: {dados_estado_atual['id']})")
        
        # Obtém as regiões imediatas para o estado atual.
        dataframe_regioes_estado = obter_regioes_imediatas_por_estado(dados_estado_atual['id'])

        # Verifica se foram encontradas regiões imediatas para o estado.
        if dataframe_regioes_estado is None:
            # Exibe uma mensagem e continua para o próximo estado se nenhuma região for encontrada.
            print(f"-> Nenhuma região imediata encontrada para o estado {dados_estado_atual['sigla']}\n")
            continue # Pula para a próxima iteração do loop 'for estado'.

        # Itera sobre cada linha (região imediata) no DataFrame de regiões imediatas do estado.
        for indice_regiao, dados_regiao_atual in dataframe_regioes_estado.iterrows():
            # Exibe qual região imediata está sendo processada.
            print(f"   Obtendo metadados da região imediata: {dados_regiao_atual['nome']} ({dados_regiao_atual['id']})...", end="")
            
            # Obtém os metadados da malha para a região imediata atual.
            metadados_malha_obtidos = obter_metadados_malha_regiao_imediata(dados_regiao_atual['id'])

            # Verifica se os metadados da malha foram obtidos com sucesso.
            if metadados_malha_obtidos is not None:
                # Cria um dicionário para armazenar os dados da região e seus metadados.
                # Inclui o ID e nome da região para facilitar a identificação futura.
                dicionario_metadados_enriquecido = {
                    "id_regiao_imediata": dados_regiao_atual['id'],
                    "nome_regiao_imediata": dados_regiao_atual['nome'],
                    "metadados_malha": metadados_malha_obtidos
                }
                # Adiciona o dicionário à lista de sucessos.
                lista_regioes_com_sucesso.append(dicionario_metadados_enriquecido)
                # Exibe " OK" na mesma linha de progresso.
                print(" OK")
            else:
                # Se a obtenção dos metadados falhou, adiciona as informações da região à lista de falhas.
                lista_regioes_com_falha.append({
                    "id_regiao_imediata": dados_regiao_atual['id'],
                    "nome_regiao_imediata": dados_regiao_atual['nome'],
                    "sigla_estado": dados_estado_atual['sigla']
                })
                # Exibe " FALHOU" na mesma linha de progresso.
                print(" FALHOU")

            # Pausa por um curto período para evitar sobrecarregar a API do IBGE.
            time.sleep(0.1) 
        # Adiciona uma linha em branco para separar a saída de cada estado.
        print("")

    # Imprime um relatório final do processamento.
    print("="*50)
    print(f"Total de regiões imediatas processadas: {len(lista_regioes_com_sucesso) + len(lista_regioes_com_falha)}")
    print(f"Regiões com metadados obtidos com sucesso: {len(lista_regioes_com_sucesso)}")
    print(f"Regiões com falha na obtenção de metadados: {len(lista_regioes_com_falha)}")

    # Salva os resultados das regiões com sucesso em um arquivo JSON.
    # Abre o arquivo no modo de escrita ('w'), com codificação UTF-8.
    with open("regioes-imediatas-metadados.json", "w", encoding="utf-8") as arquivo_saida_json:
        # Salva a lista de dicionários no formato JSON.
        # `ensure_ascii=False` permite caracteres não-ASCII (acentos, etc.).
        # `indent=2` formata o JSON com indentação para legibilidade.
        json.dump(lista_regioes_com_sucesso, arquivo_saida_json, ensure_ascii=False, indent=2)
    # Exibe uma mensagem confirmando o salvamento do arquivo.
    print("Arquivo 'regioes-imediatas-metadados.json' salvo com os metadados obtidos.")

    # Se houver regiões que falharam, imprime uma lista detalhada.
    if lista_regioes_com_falha:
        print("\nLista de regiões imediatas com falha ao obter metadados:")
        for regiao_com_erro in lista_regioes_com_falha:
            # Imprime as informações de cada região que falhou.
            print(f" - {regiao_com_erro['nome_regiao_imediata']} (ID: {regiao_com_erro['id_regiao_imediata']}, Estado: {regiao_com_erro['sigla_estado']})")


# --- Bloco Principal de Execução ---
# Este bloco é executado apenas quando o script é rodado diretamente.
if __name__ == "__main__":
    # Chama a função principal que orquestra todo o processo de coleta e salvamento de dados.
    coletar_e_salvar_dados_regioes_imediatas()