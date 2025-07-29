import requests
import pandas as pd

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
API_TIMEOUT = 30

def _fetch_request(url: str):
    """Helper function to make GET requests with standardized error handling."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=API_TIMEOUT)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\nAPI ERROR at URL {url}: {e}")
        return None

def fetch_states():
    """Fetches all Brazilian states and returns them as a DataFrame."""
    data = _fetch_request("https://servicodados.ibge.gov.br/api/v1/localidades/estados")
    if data:
        df = pd.DataFrame(data)[['id', 'sigla', 'nome']]
        df = df.rename(columns={'sigla': 'abbreviation', 'nome': 'name'})
        df['id'] = df['id'].astype(str)
        return df
    return None

def fetch_municipalities_by_state(state_abbreviation: str):
    """Fetches the municipalities of a state and returns them as a DataFrame."""
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{state_abbreviation}/municipios"
    data = _fetch_request(url)
    if data:
        df = pd.DataFrame(data)[['id', 'nome']]
        df = df.rename(columns={'nome': 'name'})
        df['id'] = df['id'].astype(str)
        return df
    return None

def fetch_regions_by_state(state_id: str, region_type: str):
    """Fetches immediate or intermediate regions of a state and returns them as a DataFrame."""
    # region_type can be 'regioes-imediatas' or 'regioes-intermediarias'
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{state_id}/{region_type}"
    data = _fetch_request(url)
    if data:
        df = pd.DataFrame(data)[['id', 'nome']]
        df = df.rename(columns={'nome': 'name'})
        df['id'] = df['id'].astype(str)
        return df
    return None

def fetch_geojson_mesh(locality_type: str, locality_id: str):
    """Gets the GeoJSON mesh for any type of locality."""
    # locality_type: 'estados', 'municipios', 'regioes-imediatas', 'regioes-intermediarias'
    base_url = "https://servicodados.ibge.gov.br/api/v2/malhas"
    if locality_type.startswith("regioes"):
        base_url = "https://servicodados.ibge.gov.br/api/v4/malhas" # API v4 for regions
        return _fetch_request(f"{base_url}/{locality_type}/{locality_id}?formato=application/vnd.geo+json")
    
    return _fetch_request(f"{base_url}/{locality_id}?formato=application/vnd.geo+json")

def fetch_population(locality_level: str, locality_id: str):
    """Gets the population for a given level (N3=state, N6=municipality) and ID."""
    url = f"https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/2021/variaveis/9324?localidades={locality_level}[{locality_id}]"
    data = _fetch_request(url)
    try:
        if data and 'resultados' in data[0] and data[0]['resultados']:
            pop_str = data[0]['resultados'][0]['series'][0]['serie']['2021']
            return int(pop_str)
        return None
    except (IndexError, KeyError, TypeError):
        return None