# Baby Foot ELO Backend

This directory contains the backend application for the Baby Foot ELO project. It is built using FastAPI and manages the game data, player rankings, and ELO calculations.

## Features

1. Player management (CRUD operations)
2. Team management (CRUD operations)
3. Match recording and ELO updates
4. Player and team ranking calculation
5. Historical ELO tracking

## Setup

To set up the backend, follow these steps:

1. Clone the repository:

```bash
git clone <https://github.com/your-repo/baby_foot_elo.git>
cd baby_foot_elo/backend
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
poetry install
```

Note: If Poetry is not installed, you can find instructions at <https://python-poetry.org/docs/#installation>.

4. Database Initialization:

The application uses DuckDB for its database. The database will be initialized automatically on startup if it doesn't exist. You can also manually run the initialization script:

```bash
poetry run python -m app.db.initializer
```

## Running the Application

To run the backend application, use Uvicorn:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- `--host 0.0.0.0`: Makes the application accessible from other devices on your network.
- `--port 8000`: Specifies the port to run the application on.
- `--reload`: Enables auto-reloading on code changes (useful for development).

The API documentation will be available at <http://localhost:8000/docs> (Swagger UI) and <http://localhost:8000/redoc> (ReDoc) once the application is running.

## Project Structure

```markdown
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/ # API endpoints for different resources
│   │   └── __init__.py
│   ├── core/ # Core configurations, settings, and utilities
│   ├── db/ # Database connection, initialization, and repositories
│   │   ├── repositories/ # Database interaction logic
│   │   └── __init__.py
│   ├── models/ # Pydantic models for request/response validation
│   ├── schema/ # Database schema definitions
│   ├── main.py # FastAPI application entry point
│   └── __init__.py
├── tests/ # Unit and integration tests
├── .env.example # Example environment variables
├── pyproject.toml # Project dependencies and metadata (Poetry/Hatch)
└── README.md # This file
```

## Dependencies

1. **FastAPI**: Web framework for building APIs.
2. **Uvicorn**: ASGI server for running the FastAPI application.
3. **DuckDB**: In-process SQL OLAP database.
4. **Pydantic**: Data validation and settings management.
5. **Loguru**: Logging library.

## API Endpoints

Details about specific API endpoints will be available in the interactive documentation at <http://localhost:8000/docs> once the application is running.
