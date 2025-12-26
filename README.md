# Baby Foot ELO

This project implements an ELO rating system for baby foot (foosball) matches. It provides a backend API for managing players, teams, and matches, and a frontend application for visualizing rankings and match history.

## Features

- Player and Team management
- ELO rating calculation for matches
- Historical ELO tracking
- Player and Team rankings
- RESTful API
- Web-based user interface

## Technologies Used

### Backend

- **Python**: Programming language
- **FastAPI**: Web framework for building APIs
- **DuckDB**: In-process SQL OLAP database management system
- **Loguru**: Logging library
- **Pydantic**: Data validation and settings management

### Frontend

- **TypeScript**: Programming language
- **React**: JavaScript library for building user interfaces
- **Next.js**: React framework for production
- **ShadCN UI**: Reusable components for React
- **Recharts**: Composable charting library built on React components

## Setup and Installation

### Prerequisites

- Python 3.9+
- Bun 1.x (or Node.js 18+ with npm)

### Backend Setup

1. Navigate to the `backend` directory:

   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations and start the application:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

### Frontend Setup

1. Navigate to the `frontend` directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   bun install
   ```

3. Start the development server:

   ```bash
   bun run dev
   ```

   The frontend application will be available at `http://localhost:3000`.

### Quick Start (Full Stack)

From the root directory, you can run both frontend and backend concurrently:

```bash
bun install          # Install root dependencies
bun run dev          # Start both servers
```

## Project Structure

```bash
.
├── backend/
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── db/              # Database initialization and repositories
│   │   ├── models/          # Pydantic models for data validation
│   │   └── main.py          # FastAPI application entry point
│   ├── tests/               # Backend tests
│   ├── requirements.txt     # Python dependencies
│   └── pyproject.toml       # Project metadata and dependencies (Poetry)
├── frontend/
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── app/             # Next.js app directory
│   │   ├── components/      # React components
│   │   ├── lib/             # Utility functions
│   │   ├── services/        # API service integrations
│   │   └── styles/          # Global styles
│   ├── tests/               # Frontend tests
│   ├── package.json         # Node.js dependencies
│   └── tsconfig.json        # TypeScript configuration
└── README.md
```
