# 🐾 PawMatch — AI-Powered Lost & Found Pet Recovery

PawMatch is a full-stack web application that helps pet owners manage lost and found reports and identify potential matches using **image-based pet embeddings, geospatial proximity, and report metadata**.

This project was built as a **personal learning project** to explore how machine learning can be integrated into a real-world web application rather than existing as an isolated model.

---

## What It Does

PawMatch connects lost and found pet reports and ranks potential matches using multiple signals:

- **Visual similarity** between pet images
- **Geographical proximity** between reports
- **Time-based relevance** of reports
- **Report metadata** such as species and descriptive information

Instead of relying on a single similarity score, the application combines these signals into a ranked set of potential matches.

---

## Features

### Lost & Found Reports

Users can create and manage reports containing:

- Pet images
- Pet details
- Location
- Date/time information
- Lost/found status

### Authentication

- User registration and login
- Password hashing
- Session-based authentication
- User-specific report management

### AI Matching Pipeline

The AI components are separated from the Flask application so that individual models can be replaced or improved independently.

The pipeline includes:

- Object detection interface
- Pet image embedding generation
- ResNet-based pet embedding model
- Visual similarity calculation
- Match ranking

### Geospatial Matching

Locations are geocoded and compared using **Haversine distance calculations**.

Geographical distance is incorporated into the overall matching score so that nearby reports can be prioritized.

### Match Ranking

Potential matches are ranked using multiple factors rather than image similarity alone.

The ranking system incorporates:

- Visual similarity
- Distance
- Time relevance
- Report information

### Notifications

The application includes an email notification component for communicating potential matches.

### Docker Support

Docker and Docker Compose configurations are included for running the application and PostgreSQL database together.

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │      Web Browser    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Flask Web App    │
                    │  Routes / Sessions  │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
      ┌─────────────┐   ┌──────────────┐  ┌─────────────┐
      │ PostgreSQL  │   │ AI Pipeline  │  │ Geocoding   │
      │  Database   │   │              │  │             │
      └─────────────┘   │ Detection    │  │ Coordinates │
                        │ Embeddings   │  │ + Distance  │
                        └──────┬───────┘  └──────┬──────┘
                               │                 │
                               └────────┬────────┘
                                        ▼
                               ┌─────────────────┐
                               │ Match / Ranking │
                               │     Engine      │
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │  Notifications  │
                               └─────────────────┘
```

The architecture intentionally keeps the **web application, database, geospatial processing, AI pipeline, matching logic, and notification system modular**.

---

## Tech Stack

| Area                  | Technology                        |
| --------------------- | --------------------------------- |
| Backend               | Python, Flask                     |
| Database              | PostgreSQL                        |
| Data Storage          | PostgreSQL JSONB                  |
| Machine Learning      | PyTorch, ResNet                   |
| Image Processing      | PIL / Python imaging tools        |
| Geospatial Processing | geopy                             |
| Authentication        | Flask sessions + password hashing |
| Notifications         | SMTP / email                      |
| Containerization      | Docker, Docker Compose            |
| Dependency Management | `uv` / `requirements.txt`         |
| Frontend              | HTML, CSS, Jinja templates        |

---

## Project Structure

```text
pawmatch/
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── report_form.html
│   ├── my_reports.html
│   └── matches.html
│
├── uploads/
│
├── app.py
├── database.py
├── schema.sql
│
├── detector.py
├── embeddings.py
├── geocoding.py
├── matcher.py
├── notifications.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/anweshasingh-dev/pawmatch.git
cd pawmatch
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```text
POSTGRES_DB=pawmatch
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Add any additional credentials required by the email/geocoding services configured in the application.

### 5. Set up PostgreSQL

Create the database and apply the schema from:

```text
schema.sql
```

Alternatively, use the included Docker Compose configuration.

### 6. Run the application

```bash
python app.py
```

The application can then be accessed through the local Flask server.

---

## Running with Docker

The repository includes:

```text
Dockerfile
docker-compose.yml
```

These provide a containerized setup for the Flask application and PostgreSQL database.

```bash
docker compose up --build
```

---

## Design Approach

One of the main goals of PawMatch was to avoid tightly coupling the machine-learning code with the web application.

For example:

```text
Flask Application
       │
       ▼
AI Interface
       │
       ├── Detection
       └── Embedding
              │
              ▼
        Matching Engine
```

This makes it possible to experiment with different models without restructuring the entire application.

The matching system also treats AI predictions as **potential matches rather than definitive identification**, allowing multiple signals to contribute to the ranking.

---

## Learning Goals

PawMatch was built primarily as a learning project.

Through the project, I explored:

- Designing a full-stack application around an ML component
- Flask application structure and routing
- PostgreSQL schema design
- JSONB data storage
- User authentication
- Image upload handling
- Geocoding and geospatial calculations
- Image embeddings and similarity
- Multi-factor ranking systems
- Email notifications
- Docker and Docker Compose
- Separating ML pipelines from application logic
- Structuring a project for future model replacement

---

## Future Improvements

The current implementation is considered complete for the scope of this project.

Possible future extensions include:

- Migrating embedding storage to **pgvector**
- Approximate nearest-neighbor vector indexing
- Improved pet-specific embedding models
- More sophisticated ranking strategies
- Better location-aware search
- Production deployment
- Improved notification workflows
- Larger-scale testing with real-world datasets

These are intentionally left as future extensions rather than requirements for the current version.

---

## Project Status

**Completed — Personal Learning Project**

PawMatch is no longer being actively developed as part of this project scope.

The codebase represents a complete learning implementation of the application's core architecture, with additional improvements such as vector indexing and production-scale infrastructure left as potential future experiments.

---

## About

I built this project to explorehow different components of a real application — **web development, databases, machine learning, geospatial processing, and backend systems** — can work together as one system. It taught me a lot along the way and was a great learning experience overall.
