"""Importing any module of this package first runs this file.

It loads the .env file and fixes DATABASE_URL (postgres:// or
postgresql:// -> postgresql+psycopg://) before the modules create their
database engines, no matter which module is imported first.
"""

from dotenv import load_dotenv

from .bootstrap import normalize_database_url_env

load_dotenv()

normalize_database_url_env()
