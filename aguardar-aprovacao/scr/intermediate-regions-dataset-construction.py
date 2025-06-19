import requests
import json
import time
import pandas as pd


def listar_estados():
    """Busca todos os estados do Brasil pela API IBGE."""
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        estados = response.json()
        df = pd.DataFrame(estados)[['id', 'sigla', 'nome']]
        df['id'] = df['id'].astype(str)
        return df
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar estados: {e}")
        return None


def listar_regioes_intermediarias_por_estado(id_estado: str):
    """Lista as regiões intermediárias de um estado pelo ID do estado."""
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{id_estado}/regioes-intermediarias"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        regioes = response.json()
        if not regioes:
            print(f"-> Nenhuma região intermediária encontrada para estado {id_estado}.")
            return None
        df = pd.DataFrame(regioes)[['id', 'nome']]
        df['id'] = df['id'].astype(str)
        return df
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar regiões intermediárias para estado {id_estado}: {e}")
        return None


def obter_malha_regiao_intermediaria(id_regiao_intermediaria: str):
    """Obtém a malha GeoJSON para uma região intermediária pelo ID."""
    url = f"https://servicodados.ibge.gov.br/api/v4/malhas/regioes-intermediarias/{id_regiao_intermediaria}?formato=application/vnd.geo+json"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


if __name__ == "__main__":
    estados_df = listar_estados()
    if estados_df is None:
        print("Erro ao obter lista de estados. Encerrando.")
        exit(1)

    regioes_sucesso = []
    regioes_falha = []

    print("Iniciando coleta de regiões intermediárias e suas malhas GeoJSON...\n")

    for _, estado in estados_df.iterrows():
        print(f"Processando estado {estado['sigla']} - {estado['nome']} (ID: {estado['id']})")
        regioes_df = listar_regioes_intermediarias_por_estado(estado['id'])

        if regioes_df is None:
            print(f"-> Nenhuma região intermediária encontrada para o estado {estado['sigla']}\n")
            continue

        for _, regiao in regioes_df.iterrows():
            print(f"  Obtendo malha da região intermediária: {regiao['nome']} ({regiao['id']})...", end="")
            malha = obter_malha_regiao_intermediaria(regiao['id'])

            if malha is not None:
                malha_enriquecida = {
                    "id": regiao['id'],
                    "nome": regiao['nome'],
                    "malha": malha
                }
                regioes_sucesso.append(malha_enriquecida)
                print(" OK")
            else:
                regioes_falha.append({"id": regiao['id'], "nome": regiao['nome'], "estado": estado['sigla']})
                print(" FALHOU")

            time.sleep(0.1)  # Pequena pausa para respeitar a API

        print("")

    print("="*50)
    print(f"Total de regiões intermediárias processadas: {len(regioes_sucesso) + len(regioes_falha)}")
    print(f"Regiões com malha obtida: {len(regioes_sucesso)}")
    print(f"Regiões com falha: {len(regioes_falha)}")

    # Salvar arquivo JSON com regiões intermediárias bem-sucedidas
    with open("regioes-intermediarias.json", "w", encoding="utf-8") as f:
        json.dump(regioes_sucesso, f, ensure_ascii=False, indent=2)
    print("Arquivo 'regioes-intermediarias.json' salvo com as malhas obtidas.")

    if regioes_falha:
        print("\nLista de regiões intermediárias com falha ao obter malha:")
        for regiao in regioes_falha:
            print(f" - {regiao['nome']} (ID: {regiao['id']}, Estado: {regiao['estado']})")
