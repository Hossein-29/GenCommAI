# GenCommAI API

A FastAPI-based API project for GenCommAI.

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Create a `.env` file:
```bash
cp .env.example .env  # If .env.example exists
# Then edit .env with your configuration
```

## Running the Application

To run the development server:

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Development

- The project uses `pyproject.toml` for dependency management
- Environment variables are managed through `.env` files
- Code formatting and linting are configured with Ruff 