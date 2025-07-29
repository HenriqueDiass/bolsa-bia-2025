import time
# Assuming the previous files were saved with the new english names
from shared.ibge_api import fetch_municipalities_by_state, fetch_geojson_mesh, fetch_population
from shared.file_utils import save_geojson

class FetchMunicipalitiesUseCase:
    """
    Use Case that fetches detailed data (mesh, population)
    for the municipalities of a given state.
    """

    def execute(self, state_abbreviation: str, output_filename: str):
        """
        Executes the data fetching for the municipalities of a state.

        :param state_abbreviation: The state's abbreviation to be processed (e.g., 'PE').
        :param output_filename: The name of the output GeoJSON file.
        """
        municipalities_df = fetch_municipalities_by_state(state_abbreviation)
        if municipalities_df is None:
            print(f"Could not retrieve the list of municipalities for {state_abbreviation}.")
            return

        features = []
        print(f"\n--- Starting data collection: MUNICIPALITY DATA FOR {state_abbreviation.upper()} ---")
        for _, municipality in municipalities_df.iterrows():
            municipality_id, name = municipality['id'], municipality['name']
            print(f"  Processing {name} ({municipality_id})... ", end="", flush=True)
            
            mesh = fetch_geojson_mesh("municipios", municipality_id)
            population_value = fetch_population("N6", municipality_id)

            if mesh and 'features' in mesh and mesh['features']:
                feature = mesh['features'][0]
                feature["properties"]["name"] = name
                
                # Same safe conversion logic for the population
                try:
                    feature["properties"]["population"] = int(population_value)
                except (ValueError, TypeError):
                    feature["properties"]["population"] = 0
                    
                features.append(feature)
                print("OK")
            else:
                print("FAILED to get mesh")
            time.sleep(0.1)
        
        save_geojson(features, output_filename)
        print(f"\n✅ Process finished. File saved at: {output_filename}")