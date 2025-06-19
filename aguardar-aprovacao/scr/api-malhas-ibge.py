import requests

url = "https://servicodados.ibge.gov.br/api/v3/malhas/estados/26"
headers = {
    "Accept": "application/vnd.svg+xml"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    with open("pe_estado.svg", "wb") as f:
        f.write(response.content)
    print("Malha do estado de Pernambuco salva com sucesso!")
else:
    print(f"Erro ao obter malha do estado: {response.status_code}")