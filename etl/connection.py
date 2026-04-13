"""
Database connection — reads DATABASE_URL from .env and returns a psycopg2 connection.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """
    Return a psycopg2 connection using DATABASE_URL from the environment.
    Raises a clear error if the variable is missing.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise EnvironmentError(
            "DATABASE_URL is not set. Copy .env.example to .env and fill in your credentials."
        )
    return psycopg2.connect(url)
