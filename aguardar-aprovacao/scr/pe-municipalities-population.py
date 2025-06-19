import requests
import time
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def listar_municipios_por_estado(sigla_uf: str):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{sigla_uf.upper()}/municipios"
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        dados = response.json()
        if not dados:
            print(f"-> AVISO: Nenhum município encontrado para a sigla {sigla_uf}.")
            return None
        return dados
    except requests.exceptions.RequestException as e:
        print(f"-> ERRO ao buscar lista de municípios: {e}")
        return None

def obter_populacao_municipio(codigo_ibge: str):
    url = (
        f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324"
        f"?localidades=N6[{codigo_ibge}]"
    )
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        dados = response.json()
        if dados:
            pop_str = dados[0]['resultados'][0]['series'][0]['serie']['2021']
            return int(pop_str)
        return None
    except (requests.exceptions.RequestException, IndexError, KeyError):
        return None

if __name__ == "__main__":
    sigla_uf = "PE"
    municipios = listar_municipios_por_estado(sigla_uf)
    if municipios is None:
        print("Não foi possível obter a lista de municípios.")
        exit()

    resultados = []
    total_municipios = len(municipios)
    # Contadores de malha removidos
    cont_populacao_encontrada = 0
    cont_populacao_nao_encontrada = 0

    print(f"Processando municípios do estado {sigla_uf}...\n")

    for municipio in sorted(municipios, key=lambda m: m['nome']):
        codigo = str(municipio['id'])
        nome = municipio['nome']


        populacao = obter_populacao_municipio(codigo)
        if populacao is not None:
            cont_populacao_encontrada += 1
        else:
            cont_populacao_nao_encontrada += 1
            populacao = 0

        print(f"{nome} ({codigo}): População {'ENCONTRADA' if populacao else 'NÃO ENCONTRADA'}")

        resultados.append({
            "municipio": nome,
            "codigoMunicipio": codigo,
            "população": populacao
            
        })

        time.sleep(0.1)

    # Salvar resultados em JSON
    with open("municipios-pe-populacao.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print("\n" + "="*50)
    print(f"Total de municípios encontrados: {total_municipios}")
    # Contadores de malha removidos do resumo final
    print(f"População encontrada para: {cont_populacao_encontrada}")
    print(f"População NÃO encontrada para: {cont_populacao_nao_encontrada}")
    print("="*50)
    print(f"Dados salvos em 'municipios-pe-populacao.json'.")