# use_cases/fetch_states/index.py

import time
# Assuming the previous files were saved with the new english names
from shared.ibge_api import fetch_states, fetch_geojson_mesh, fetch_population
from shared.file_utils import save_geojson

class FetchStatesUseCase:
    """
    Use Case that fetches detailed data (mesh, population)
    for all states of Brazil and saves the result to a GeoJSON file.
    """
    
    def execute(self, output_filename: str):
        """
        Executes the use case.

        :param output_filename: The name of the output GeoJSON file.
        """
        states_df = fetch_states()
        if states_df is None:
            print("Could not retrieve the list of states. Aborting.")
            return

        features = []
        print("\n--- Starting data collection: COMPLETE DATA BY STATE ---")
        for _, state in states_df.iterrows():
            state_id, abbreviation, name = state['id'], state['abbreviation'], state['name']
            print(f"Processing {name} ({abbreviation})... ", end="", flush=True)
            
            mesh = fetch_geojson_mesh("estados", state_id)
            population_value = fetch_population("N3", state_id)

            if mesh and 'features' in mesh and mesh['features']:
                feature = mesh['features'][0]
                feature['properties']['abbreviation'] = abbreviation
                feature['properties']['name'] = name
                
                # --- FIXED CODE ---
                # Safe conversion logic for the population
                try:
                    # Tries to convert the value to an integer. Works for ints (e.g., 5) and strings (e.g., "5").
                    feature['properties']['population_2021'] = int(population_value)
                except (ValueError, TypeError):
                    # If the conversion fails (e.g., value is None or an empty string), use 0.
                    feature['properties']['population_2021'] = 0
                
                features.append(feature)
                print("OK")
            else:
                print("FAILED to get mesh")
            time.sleep(0.1)

        save_geojson(features, output_filename)
        print(f"\n✅ Process finished. File saved at: {output_filename}")