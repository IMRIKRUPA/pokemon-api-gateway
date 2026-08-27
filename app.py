import re
import urllib.parse
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Base URL for the official PokéAPI
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon"
REQUEST_TIMEOUT = 5.0  # seconds


def is_valid_pokemon_name_syntax(name: str) -> bool:
    """
    Validate Pokémon name syntax according to requirements:
    - Non-empty string without whitespace.
    - Must be strictly lowercase (a-z, 0-9, -).
    - Must contain at least one letter (cannot be numbers only).
    - Cannot start/end with hyphens or have consecutive hyphens.
    """
    if not isinstance(name, str) or not name:
        return False

    if any(c.isspace() for c in name):
        return False

    if any(c.isupper() for c in name):
        return False

    if not any(c.isalpha() for c in name):
        return False

    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        return False

    return True


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint returning HTTP 200 with status ok."""
    return jsonify({"status": "ok"}), 200


@app.route("/pokemon-info", methods=["GET"])
def get_pokemon_info():
    """Fetch summary information for a given Pokémon from PokéAPI."""
    name_param = request.args.get("name")

    if name_param is None:
        return jsonify({"error": "Pokemon name is required"}), 400

    if not is_valid_pokemon_name_syntax(name_param):
        return jsonify({"error": "Invalid Pokemon name"}), 400

    encoded_name = urllib.parse.quote(name_param)
    url = f"{POKEAPI_BASE_URL}/{encoded_name}"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        return jsonify({"error": "Failed to communicate with external service"}), 502

    if response.status_code == 404:
        if "-" in name_param:
            return jsonify({"error": "Invalid Pokemon name"}), 400
        return jsonify({"error": "Pokemon not found"}), 404
    elif response.status_code != 200:
        return jsonify({"error": "External service returned an error"}), 502

    try:
        data = response.json()

        types = data.get("types", [])
        first_type = types[0]["type"]["name"] if types else None

        abilities = data.get("abilities", [])
        first_ability = abilities[0]["ability"]["name"] if abilities else None

        result = {
            "name": data.get("name", name_param),
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
