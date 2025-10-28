import requests
import json
from typing import Dict, Any, List

API_BASE_URL = "https://www.arrow.it/api/en/marche/list"
OUTPUT_FILE = "arrow_structure_initial.json"


def fetch_brands() -> List[Dict[str, Any]]:
    """
    Fetch the list of motorcycle brands from the Arrow API.

    Returns:
        List of brand objects (dicts) containing brand IDs and names.
    Raises:
        Exception: If the HTTP request fails or the response is invalid.
    """
    try:
        response = requests.get(API_BASE_URL, timeout=10)
        response.raise_for_status()
        brands = response.json()
        if not isinstance(brands, list):
            raise Exception("Invalid response format for brands list.")
        return brands
    except requests.RequestException as e:
        print(f"Error fetching brands: {e}")
        return []


def fetch_models(brand_id: int) -> List[Dict[str, Any]]:
    """
    Fetch the list of models for a given brand from the Arrow API.

    Args:
        brand_id (int): The ID of the brand.

    Returns:
        List of model objects (dicts) for the specified brand.
    Raises:
        Exception: If the HTTP request fails or the response is invalid.
    """
    url = f"{API_BASE_URL}/{brand_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        models = response.json()
        if not isinstance(models, list):
            raise Exception(f"Invalid response format for models of brand {brand_id}.")
        return models
    except requests.RequestException as e:
        print(f"Error fetching models for brand {brand_id}: {e}")
        return []


def build_hierarchical_data() -> Dict[str, Any]:
    """
    Build a hierarchical dictionary mapping each brand to its models.

    Returns:
        Dictionary where keys are brand names, and values are lists of model names.
    """
    print("Fetching brands...")
    brands = fetch_brands()
    hierarchy = {}

    for brand in brands:
        brand_id = brand.get("id")
        brand_name = brand.get("name") or brand.get("nome")  # Handle possible localization
        if brand_id is None or brand_name is None:
            continue  # Skip if essential data is missing

        print(f"Fetching models for brand: {brand_name} (ID: {brand_id})")
        models = fetch_models(brand_id)
        # Extract model names or use the entire model dict if needed
        model_names = [model.get("name") or model.get("nome") for model in models if model.get("name") or model.get("nome")]
        hierarchy[brand_name] = model_names

    return hierarchy


def save_to_json(data: Dict[str, Any], filename: str) -> None:
    """
    Save the given dictionary data to a JSON file.

    Args:
        data (dict): The data to save.
        filename (str): The filename to write to.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved successfully to {filename}")
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")


def main():
    """
    Main entry point for the script.
    Fetches the hierarchical brands and models data and saves it as JSON.
    """
    print("Starting Arrow API scraper...")
    hierarchy = build_hierarchical_data()
    save_to_json(hierarchy, OUTPUT_FILE)
    print("Scraping completed.")


if __name__ == "__main__":
    main()