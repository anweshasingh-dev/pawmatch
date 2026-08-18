import os
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import json
from dotenv import load_dotenv

load_dotenv()

# Update with your local PostgreSQL credentials or environment variable
DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB", "pawmatch"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", ""),
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": os.environ.get("POSTGRES_PORT", "5432")
}

def get_db_connection():
    """Returns a new PostgreSQL connection with dictionary cursor capabilities."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(name: str, email: str, password: str) -> bool:
    """Registers a new user."""
    pwd_hash = hash_password(password)
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                    (name, email.strip().lower(), pwd_hash)
                )
                conn.commit()
                return True
    except psycopg2.IntegrityError:
        return False

def verify_user(email: str, password: str):
    """Verifies user credentials."""
    pwd_hash = hash_password(password)
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email FROM users WHERE email = %s AND password_hash = %s",
                (email.strip().lower(), pwd_hash)
            )
            user = cursor.fetchone()
            return dict(user) if user else None

def save_report(data: dict) -> int:
    query = """
    INSERT INTO reports (
        user_id, type, species, pet_name, breed, color, distinctive_marks,
        contact_name, contact_phone, contact_email, address, latitude, longitude,
        event_date, description, image_path, image_vector
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id;
    """
    params = (
        data.get("user_id"),
        data.get("type"),
        data.get("species"),
        data.get("pet_name"),
        data.get("breed"),
        data.get("color"),
        data.get("distinctive_marks"),
        data.get("contact_name"),
        data.get("contact_phone"),
        data.get("contact_email"),
        data.get("address"),
        data.get("latitude"),
        data.get("longitude"),
        data.get("event_date"),
        data.get("description"),
        data.get("image_path"),
        json.dumps(data.get("image_vector")) if data.get("image_vector") else None
    )
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            report_id = cursor.fetchone()["id"]
            conn.commit()
            return report_id

def update_report_status(report_id: int, status: str):
    """Updates report status."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE reports SET status = %s WHERE id = %s", (status, report_id))
            conn.commit()

def get_active_reports():
    query = "SELECT * FROM reports WHERE status = 'ACTIVE' ORDER BY created_at DESC;"
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()