import json

def save_geojson(features: list, output_filename: str):
    """
    Creates a FeatureCollection object and saves it to a .geojson file.
    """
    if not output_filename.endswith(".geojson"):
        output_filename += ".geojson"

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(feature_collection, f, ensure_ascii=False, indent=2)
        print(f"\nFile '{output_filename}' saved successfully!")
        print(f"Total features saved: {len(features)}")
    except IOError as e:
        print(f"\nError saving file '{output_filename}': {e}")