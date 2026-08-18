# 🐾 PawMatch - AI Pet Recovery Platform (Work in Progress)

PawMatch is a full-stack web application designed to help owners locate lost pets by cross-referencing lost and found reports using location tracking, feature embeddings, and relational database management.

> **Project Status:** Work in Progress (WIP). Core web infrastructure, database schema, geocoding, and decoupled AI pipeline interfaces are implemented.

---

## Features Implemented

- **Flask Web Server:** Modular routing for reporting lost/found pets and browsing listings.
- **PostgreSQL Database:** Relational schema supporting user reports and JSONB vector storage.
- **Geospatial Distance Scoring:** Haversine distance calculations powered by `geopy` for local proximity weighting.
- **Decoupled AI Pipeline:** Pluggable mock detection interface (`detector.py`) designed for easy swapping with a custom-trained vision model.
- **Containerization:** Docker & Docker Compose setup for database and application orchestration.

---

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/pawmatch.git](https://github.come/anweshasingh-dev/pawmatch.git)
   cd pawmatch
   Set up Virtual Environment:
   ```

```bash
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory:
```

```text
Code snippet
POSTGRES_DB=pawmatch
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
Run Application:
```

```bash
python app.py
```

## Upcoming Roadmap

- [ ] **Custom ML Engine:** Train and integrate a custom pet detection model to replace the current stub interface.
- [ ] **Enhanced Ranking Engine:** Fine-tune similarity algorithms across vector embeddings and time-decay metrics.

- [ ] **UI/UX Polishing:** Redesign user forms and dashboard views using styled CSS components.

- [ ] **Authentication:** Implement full user registration, password hashing, and session persistence.
