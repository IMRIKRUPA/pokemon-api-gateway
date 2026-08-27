# Pokémon API Gateway

A production-ready Flask REST API gateway that interfaces with the official [PokéAPI](https://pokeapi.co/) to fetch and summarize Pokémon information.

---

## Features

- **Health Check**: `GET /health` returns application operational status.
- **Pokémon Info Lookup**: `GET /pokemon-info?name={pokemon_name}` returns normalized Pokémon details (`name`, `type`, `height`, `weight`, `first_ability`).
- **Input Normalization**: Trims whitespace and normalizes Pokémon names to lowercase.
- **Robust Error Handling**: Standardized JSON responses for missing arguments (`400`), missing Pokémon (`404`), unsupported HTTP methods (`405`), and external service errors (`502`).
- **JSON Standard**: All API endpoints and error responses strictly return `Content-Type: application/json`.
- **Vercel Ready**: Pre-configured serverless setup via `vercel.json`.

---

## API Endpoints

### 1. GET `/health`
Returns the status of the gateway service.

**Response `200 OK`**:
```json
{
  "status": "ok"
}
```

---

### 2. GET `/pokemon-info?name={pokemon_name}`
Fetches details for the specified Pokémon.

**Query Parameters**:
- `name` *(required)*: The name of the Pokémon (case-insensitive).

**Response `200 OK`**:
```json
{
  "name": "ditto",
  "type": "normal",
  "height": 3,
  "weight": 40,
  "first_ability": "limber"
}
```

**Error Responses**:

- **Missing Name Parameter (`400 Bad Request`)**:
  ```json
  {
    "error": "Pokemon name is required"
  }
  ```

- **Pokémon Not Found (`404 Not Found`)**:
  ```json
  {
    "error": "Pokemon not found"
  }
  ```

- **External PokéAPI Failure (`502 Bad Gateway`)**:
  ```json
  {
    "error": "Failed to communicate with external service"
  }
  ```

- **Method Not Allowed (`405 Method Not Allowed`)**:
  ```json
  {
    "error": "Method not allowed"
  }
  ```

---

## Local Setup & Development

### Prerequisites
- Python 3.9+
- `pip`

### Installation

1. Clone the repository and navigate into the directory:
   ```bash
   git clone <repository-url>
   cd pokemon-api-gateway
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Flask application:
   ```bash
   python3 app.py
   ```
   The API will be live at `http://127.0.0.1:5000`.

---

## Running Tests

Automated tests use `pytest` and mock external requests to PokéAPI.

Run all tests with:
```bash
pytest
```

---

## Deploying to Vercel

You can deploy this application to Vercel using either the **Vercel CLI** or **GitHub Integration**.

### Option A: Deploying via Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy to Preview**:
   Run the following command from the project root directory:
   ```bash
   vercel
   ```
   Follow the interactive CLI prompts (accept default project settings).

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

---

### Option B: Deploying via Vercel Dashboard (GitHub / Git Integration)

1. Push your codebase to a GitHub, GitLab, or Bitbucket repository.
2. Log in to your [Vercel Dashboard](https://vercel.com/dashboard).
3. Click **Add New** -> **Project**.
4. Import your `pokemon-api-gateway` repository.
5. Vercel automatically detects `vercel.json` and configures the build settings.
6. Click **Deploy**. Vercel will deploy your Flask app as a serverless function and provide a public URL (e.g., `https://pokemon-api-gateway.vercel.app`).
