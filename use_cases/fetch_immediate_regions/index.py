import time
# Assuming the previous files were saved with the new english names
from shared.ibge_api import fetch_states, fetch_regions_by_state, fetch_geojson_mesh
from shared.file_utils import save_geojson

class FetchImmediateRegionsUseCase:
    """
    Use Case that orchestrates fetching data for all immediate
    regions of Brazil and saves the result to a GeoJSON file.
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
        print("\n--- Starting data collection: BRAZIL'S IMMEDIATE REGIONS ---")
        for _, state in states_df.iterrows():
            print(f"Processing state: {state['abbreviation']}")
            regions_df = fetch_regions_by_state(state['id'], 'regioes-imediatas')
            if regions_df is None: continue

            for _, region in regions_df.iterrows():
                region_id, region_name = region['id'], region['name']
                print(f"  Fetching mesh for {region_name}... ", end="", flush=True)
                mesh = fetch_geojson_mesh('regioes-imediatas', region_id)

                if mesh and 'features' in mesh and mesh['features']:
                    feature = mesh['features'][0]
                    # Add properties to the GeoJSON feature
                    feature['properties']['immediate_region_id'] = region_id
                    feature['properties']['immediate_region_name'] = region_name
                    feature['properties']['state_abbreviation'] = state['abbreviation']
                    features.append(feature)
                    print("OK")
                else:
                    print("FAILED to get mesh")
                time.sleep(0.1)
        
        # The filename is now a parameter, making the function reusable!
        save_geojson(features, output_filename)
        print(f"\n✅ Process finished. File saved at: {output_filename}")