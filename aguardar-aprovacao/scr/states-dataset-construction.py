import geopandas as gpd
import requests
import json
import time

def buscar_estados_brasileiros():
    """
    Busca a lista completa de Unidades Federativas (estados) do Brasil na API do IBGE.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário contém 'id' e 'sigla'
              de cada estado, ou None se ocorrer um erro ou nenhum estado for encontrado.
    """
    # Define a URL da API do IBGE para listar os estados.
    url_api_estados = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    # Exibe uma mensagem informando que a busca está sendo realizada.
    print("Buscando lista de estados do Brasil na API de Localidades do IBGE...")

    try:
        # Realiza uma requisição GET para a URL da API.
        # O 'timeout' define o tempo máximo de espera pela resposta em segundos.
        resposta_requisicao = requests.get(url_api_estados, timeout=30)
        # Levanta uma exceção HTTPError para códigos de status de erro (4xx ou 5xx).
        resposta_requisicao.raise_for_status()
        # Converte a resposta JSON da API em um objeto Python (lista de dicionários).
        dados_estados_json = resposta_requisicao.json()

        # Verifica se a lista de dados de estados está vazia.
        if not dados_estados_json:
            # Exibe um aviso se nenhum estado for encontrado.
            print("-> AVISO: Nenhum estado encontrado.")
            # Retorna None, indicando que a operação não encontrou dados.
            return None

        # Cria uma lista de dicionários, onde cada dicionário contém o 'id' (convertido para string)
        # e a 'sigla' de cada estado, extraídos dos dados JSON.
        lista_de_estados = [{'id': str(estado['id']), 'sigla': estado['sigla']} for estado in dados_estados_json]
        # Exibe uma mensagem de sucesso, informando quantos estados foram encontrados.
        print(f"-> Sucesso! {len(lista_de_estados)} estados encontrados.")
        # Retorna a lista de estados.
        return lista_de_estados

    except requests.exceptions.RequestException as erro_requisicao:
        # Captura qualquer exceção que ocorra durante a requisição (ex: problemas de conexão, timeout).
        # Exibe uma mensagem de erro detalhada.
        print(f"-> ERRO ao buscar lista de estados: {erro_requisicao}")
        # Retorna None em caso de falha.
        return None

def obter_malha_geografica_estado(codigo_ibge_estado):
    """
    Busca a malha geográfica (GeoJSON) de um estado brasileiro na API de Malhas do IBGE.

    Args:
        codigo_ibge_estado (str): O código IBGE do estado.

    Returns:
        dict: O GeoJSON da malha do estado, ou None se não encontrado ou ocorrer um erro.
    """
    # Define a URL da API de malhas do IBGE, formatando com o código do estado e o formato desejado (GeoJSON).
    url_api_malha_estado = f"https://servicodados.ibge.gov.br/api/v2/malhas/{codigo_ibge_estado}?formato=application/vnd.geo+json"

    try:
        # Realiza uma requisição GET para a URL da malha do estado.
        # O 'timeout' define o tempo máximo de espera pela resposta em segundos.
        resposta_malha = requests.get(url_api_malha_estado, timeout=15)
        # Verifica se o código de status da resposta é 404 (Não Encontrado).
        if resposta_malha.status_code == 404:
            # Retorna None se o estado não for encontrado na API de Malhas.
            return None
        # Levanta uma exceção HTTPError para códigos de status de erro (4xx ou 5xx).
        resposta_malha.raise_for_status()
        # Converte a resposta JSON da API em um objeto Python (dicionário GeoJSON).
        return resposta_malha.json()
    except requests.exceptions.RequestException:
        # Captura qualquer exceção que ocorra durante a requisição.
        # Retorna None em caso de falha.
        return None




### Bloco Principal de Execução (`if __name__ == "__main__":`)

#Este bloco é o ponto de entrada principal do programa. O código dentro dele só será executado quando o script for rodado diretamente (não quando for importado como um módulo em outro script).
# --- ROTINA PRINCIPAL DE VERIFICAÇÃO PARA ESTADOS ---
if __name__ == "__main__":
    # 1. Obter a lista completa de estados
    # Chama a função para buscar a lista de todos os estados brasileiros.
    lista_de_todos_os_estados = buscar_estados_brasileiros()

    # Verifica se a lista de estados foi obtida com sucesso (não é None).
    if lista_de_todos_os_estados is not None:
        # Inicializa uma lista para armazenar os dados dos estados que tiveram sucesso na obtenção da malha.
        estados_com_malha_sucesso = []
        # Inicializa uma lista para armazenar os dados dos estados que falharam na obtenção da malha.
        estados_com_malha_falha = []

        # Exibe uma mensagem indicando o início do processo de verificação.
        print("\n--- Iniciando a verificação da malha de cada estado ---")
        
        # Itera sobre cada dicionário de estado na lista de estados obtida.
        for estado_atual in lista_de_todos_os_estados:
            # Extrai o código IBGE do estado (ID) do dicionário.
            codigo_ibge_do_estado = estado_atual['id']
            # Extrai a sigla do estado do dicionário.
            sigla_do_estado = estado_atual['sigla']

            # Exibe uma mensagem de progresso, sem quebrar a linha.
            print(f"Verificando malha de {sigla_do_estado} (Código: {codigo_ibge_do_estado})...", end="")

            # Chama a função para obter a malha geográfica do estado atual.
            resultado_malha_geo = obter_malha_geografica_estado(codigo_ibge_do_estado)

            # Verifica se a malha geográfica foi obtida com sucesso (não é None).
            if resultado_malha_geo is not None:
                # Adiciona a sigla do estado dentro do dicionário GeoJSON para identificação futura.
                # Verifica se 'features' existe e não está vazio no GeoJSON.
                if 'features' in resultado_malha_geo and resultado_malha_geo['features']:
                    # Atribui a sigla do estado à propriedade 'sigla' do primeiro elemento 'feature'.
                    resultado_malha_geo['features'][0]['properties']['sigla'] = sigla_do_estado
                    # Adiciona o primeiro elemento 'feature' (que contém a geometria e propriedades)
                    # à lista de estados com sucesso.
                    estados_com_malha_sucesso.append(resultado_malha_geo['features'][0])
                    # Exibe " OK!" na mesma linha de progresso.
                    print(" OK!")
                else:
                    # Se 'features' estiver ausente ou vazio, indica falha.
                    print(" FALHOU (sem features)")
                    # Adiciona o estado à lista de falhas.
                    estados_com_malha_falha.append({'sigla': sigla_do_estado, 'codigo': codigo_ibge_do_estado})
            else:
                # Se a função 'obter_malha_geografica_estado' retornou None, indica falha.
                print(" FALHOU!")
                # Adiciona o estado à lista de falhas.
                estados_com_malha_falha.append({'sigla': sigla_do_estado, 'codigo': codigo_ibge_do_estado})

            # Pausa por um curto período para evitar sobrecarregar a API do IBGE.
            time.sleep(0.1)

        # 3. Imprimir relatório final
        # Imprime uma linha separadora para o relatório.
        print("\n" + "="*50)
        # Imprime o cabeçalho do relatório.
        print("--- RELATÓRIO FINAL DA VERIFICAÇÃO ---")
        # Imprime o total de estados que foram verificados.
        print(f"Total de estados verificados: {len(lista_de_todos_os_estados)}")
        # Imprime a quantidade de estados cuja malha foi encontrada com sucesso.
        print(f"Estados encontrados com sucesso: {len(estados_com_malha_sucesso)}")
        # Imprime a quantidade de estados que apresentaram falha ou dados faltantes na API.
        print(f"Estados com dados FALTANTES na API: {len(estados_com_malha_falha)}")

        # 4. Salvar resultados em arquivo JSON
        # Abre um arquivo JSON no modo de escrita ('w'), com codificação UTF-8 para suportar caracteres especiais.
        # 'ensure_ascii=False' permite que caracteres não-ASCII sejam gravados diretamente.
        # 'indent=2' formata o JSON com indentação de 2 espaços para melhor legibilidade.
        with open("dataset-estados-brasil.json", "w", encoding="utf-8") as arquivo_json_saida:
            # Salva a lista de GeoJSONs dos estados com sucesso no arquivo.
            json.dump(estados_com_malha_sucesso, arquivo_json_saida, ensure_ascii=False, indent=2)
        # Exibe uma mensagem informando que o arquivo foi salvo.
        print("Arquivo JSON salvo como 'dataset-estados-brasil.json'")

        # Verifica se houve estados com falha.
        if estados_com_malha_falha:
            # Se sim, imprime um cabeçalho para a lista de falhas.
            print("\nLista de estados que FALHARAM:")
            # Itera sobre cada estado que falhou.
            for estado_falho in estados_com_malha_falha:
                # Imprime a sigla e o código IBGE do estado que falhou.
                print(f"   - {estado_falho['sigla']} (Código: {estado_falho['codigo']})")