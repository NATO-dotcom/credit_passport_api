import psycopg2
import os

def get_db_connection():
    # This pulls your Neon connection string safely from the environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("FATAL ERROR: DATABASE_URL is missing.")
    
    # Establishes the physical link to your cloud database
    conn = psycopg2.connect(db_url)
    return conn