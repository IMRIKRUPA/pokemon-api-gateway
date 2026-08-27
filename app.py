import urllib.parse
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Base URL for the official PokéAPI
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"
REQUEST_TIMEOUT = 5.0  # seconds


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint returning HTTP 200 with status ok."""
    return jsonify({"status": "ok"}), 200


@app.route("/pokemon-info", methods=["GET"])
def get_pokemon_info():
    """Fetch summary information for a given Pokémon from PokéAPI."""
    name_param = request.args.get("name")

    if not name_param or not name_param.strip():
        return jsonify({"error": "Pokemon name is required"}), 400

    normalized_name = name_param.strip().lower()
    encoded_name = urllib.parse.quote(normalized_name)
    url = f"{POKEAPI_BASE_URL}/{encoded_name}"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        # Handle connection errors, timeouts, and network issues
        return jsonify({"error": "Failed to communicate with external service"}), 502

    if response.status_code == 404:
        return jsonify({"error": "Pokemon not found"}), 404
    elif response.status_code != 200:
        return jsonify({"error": "External service returned an error"}), 502

    try:
        data = response.json()
        
        # Extract first type and first ability safely
        types = data.get("types", [])
        first_type = types[0]["type"]["name"] if types else None

        abilities = data.get("abilities", [])
        first_ability = abilities[0]["ability"]["name"] if abilities else None

        result = {
            "name": data.get("name", normalized_name),
            "type": first_type,
            "height": data.get("height"),
            "weight": data.get("weight"),
            "first_ability": first_ability,
        }

        return jsonify(result), 200
    except (ValueError, KeyError, IndexError, TypeError):
        return jsonify({"error": "Error processing Pokemon data from external service"}), 502


@app.errorhandler(405)
def method_not_allowed(e):
    """Handle unsupported HTTP methods with JSON response."""
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(404)
def resource_not_found(e):
    """Handle 404 Not Found errors with JSON response."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 Internal Server Error without exposing stack traces."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

