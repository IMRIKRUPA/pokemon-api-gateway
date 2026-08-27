from unittest.mock import MagicMock, patch
import pytest
import requests
from app import app


@pytest.fixture
def client():
    """Flask test client fixture."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Mock response data for PokéAPI calls
DITTO_POKEAPI_RESPONSE = {
    "name": "ditto",
    "height": 3,
    "weight": 40,
    "types": [
        {"slot": 1, "type": {"name": "normal", "url": "https://pokeapi.co/api/v2/type/1/"}}
    ],
    "abilities": [
        {"ability": {"name": "limber", "url": "https://pokeapi.co/api/v2/ability/7/"}, "is_hidden": False, "slot": 1}
    ],
}

PIKACHU_POKEAPI_RESPONSE = {
    "name": "pikachu",
    "height": 4,
    "weight": 60,
    "types": [
        {"slot": 1, "type": {"name": "electric", "url": "https://pokeapi.co/api/v2/type/13/"}}
    ],
    "abilities": [
        {"ability": {"name": "static", "url": "https://pokeapi.co/api/v2/ability/9/"}, "is_hidden": False, "slot": 1},
        {"ability": {"name": "lightning-rod", "url": "https://pokeapi.co/api/v2/ability/31/"}, "is_hidden": True, "slot": 3}
    ],
}

HO_OH_POKEAPI_RESPONSE = {
    "name": "ho-oh",
    "height": 38,
    "weight": 1990,
    "types": [
        {"slot": 1, "type": {"name": "fire", "url": "https://pokeapi.co/api/v2/type/10/"}}
    ],
    "abilities": [
        {"ability": {"name": "pressure", "url": "https://pokeapi.co/api/v2/ability/46/"}, "is_hidden": False, "slot": 1}
    ],
}


def test_health_endpoint(client):
    """Test GET /health returns HTTP 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {"status": "ok"}


@patch("requests.get")
def test_pokemon_info_ditto(mock_get, client):
    """Test GET /pokemon-info?name=ditto with mocked PokéAPI response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = DITTO_POKEAPI_RESPONSE
    mock_get.return_value = mock_response

    response = client.get("/pokemon-info?name=ditto")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "name": "ditto",
        "type": "normal",
        "height": 3,
        "weight": 40,
        "first_ability": "limber",
    }
    mock_get.assert_called_once_with("https://pokeapi.co/api/v2/pokemon/ditto", timeout=5.0)


@patch("requests.get")
def test_pokemon_info_pikachu(mock_get, client):
    """Test GET /pokemon-info?name=pikachu with mocked PokéAPI response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = PIKACHU_POKEAPI_RESPONSE
    mock_get.return_value = mock_response

    response = client.get("/pokemon-info?name=pikachu")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "name": "pikachu",
        "type": "electric",
        "height": 4,
        "weight": 60,
        "first_ability": "static",
    }
    mock_get.assert_called_once_with("https://pokeapi.co/api/v2/pokemon/pikachu", timeout=5.0)


@patch("requests.get")
def test_pokemon_info_valid_hyphenated(mock_get, client):
    """Test valid hyphenated names like ho-oh."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = HO_OH_POKEAPI_RESPONSE
    mock_get.return_value = mock_response

    response = client.get("/pokemon-info?name=ho-oh")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {
        "name": "ho-oh",
        "type": "fire",
        "height": 38,
        "weight": 1990,
        "first_ability": "pressure",
    }


def test_pokemon_info_uppercase_rejected(client):
    """Test GET /pokemon-info?name=PIKACHU returns 400 Invalid Pokemon name."""
    response = client.get("/pokemon-info?name=PIKACHU")
    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Invalid Pokemon name"}


def test_pokemon_info_mixedcase_rejected(client):
    """Test GET /pokemon-info?name=Pikachu returns 400 Invalid Pokemon name."""
    response = client.get("/pokemon-info?name=Pikachu")
    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Invalid Pokemon name"}


def test_pokemon_info_numeric_only_rejected(client):
    """Test GET /pokemon-info?name=123 returns 400 Invalid Pokemon name."""
    response = client.get("/pokemon-info?name=123")
    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Invalid Pokemon name"}


def test_pokemon_info_whitespace_rejected(client):
    """Test GET /pokemon-info with whitespace returns 400 Invalid Pokemon name."""
    response = client.get("/pokemon-info?name=%20ditto%20")
    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Invalid Pokemon name"}


def test_pokemon_info_empty_string_rejected(client):
    """Test GET /pokemon-info with empty name string returns 400 Invalid Pokemon name."""
    response = client.get("/pokemon-info?name=")
    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Invalid Pokemon name"}


def test_pokemon_info_missing_name_parameter(client):
    """Test GET /pokemon-info without name parameter returns 400 Pokemon name is required."""
    response = client.get("/pokemon-info")
    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Pokemon name is required"}


@patch("requests.get")
def test_pokemon_info_malformed_hyphenated_pika_chu(mock_get, client):
    """Test malformed hyphenated name pika-chu returns 400 Invalid Pokemon name."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    response = client.get("/pokemon-info?name=pika-chu")
    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Invalid Pokemon name"}


@patch("requests.get")
def test_pokemon_info_malformed_hyphenated_a_b_c_d(mock_get, client):
    """Test malformed hyphenated name a-b-c-d returns 400 Invalid Pokemon name."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    response = client.get("/pokemon-info?name=a-b-c-d")
    assert response.status_code == 400
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Invalid Pokemon name"}


@patch("requests.get")
def test_pokemon_info_not_found_syntactically_valid(mock_get, client):
    """Test GET /pokemon-info for syntactically valid non-existent single lowercase name returns 404."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    response = client.get("/pokemon-info?name=invalidpokemon12345")
    assert response.status_code == 404
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Pokemon not found"}


@patch("requests.get")
def test_pokemon_info_external_api_failure(mock_get, client):
    """Test GET /pokemon-info when PokéAPI returns HTTP 500 error."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    response = client.get("/pokemon-info?name=ditto")
    assert response.status_code == 502
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "External service returned an error"}


@patch("requests.get")
def test_pokemon_info_timeout_exception(mock_get, client):
    """Test GET /pokemon-info when external call times out."""
    mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

    response = client.get("/pokemon-info?name=ditto")
    assert response.status_code == 502
    assert response.content_type == "application/json"
    assert response.get_json() == {"error": "Failed to communicate with external service"}


def test_unsupported_http_methods(client):
    """Test POST/PUT/DELETE requests return HTTP 405 Method Not Allowed."""
    methods = [client.post, client.put, client.delete]
    for method in methods:
        health_resp = method("/health")
        assert health_resp.status_code == 405
        assert health_resp.content_type == "application/json"
        assert health_resp.get_json() == {"error": "Method not allowed"}

        info_resp = method("/pokemon-info?name=ditto")
        assert info_resp.status_code == 405
        assert info_resp.content_type == "application/json"
        assert info_resp.get_json() == {"error": "Method not allowed"}
