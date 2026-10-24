"""Database bootstrap.

Creates the PostgreSQL schema (with pgvector) and loads the jobs, their
embeddings and their required skills, so the app can start on a brand new,
empty database (for example a fresh Neon database on Render).

Everything here is idempotent: running it again changes nothing.
"""

import json
import logging
import os
from pathlib import Path

from sqlalchemy import text


logger = logging.getLogger("semantic-search")


# ==========================================
# Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

JOBS_PATH = BASE_DIR / "data" / "jobs" / "jobs.json"

CV_PROFILE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "candidate_profile.json"
)


# ==========================================
# Database URL
# ==========================================

def normalize_database_url(url):

    """Make a provider URL work with SQLAlchemy + psycopg 3.

    Neon / Render give URLs that start with postgres:// or postgresql://.
    SQLAlchemy needs postgresql+psycopg:// to use psycopg 3.
    """

    url = url.strip().strip('"').strip("'")

    if url.startswith("postgres://"):

        url = "postgresql://" + url[len("postgres://"):]

    if url.startswith("postgresql://"):

        url = (
            "postgresql+psycopg://"
            + url[len("postgresql://"):]
        )

    return url


def normalize_database_url_env():

    url = os.getenv("DATABASE_URL")

    if url:

        os.environ["DATABASE_URL"] = (
            normalize_database_url(url)
        )


# ==========================================
# Schema
# ==========================================

# all-MiniLM-L6-v2 produces 384 dimensional vectors
EMBEDDING_DIMENSIONS = 384

SCHEMA_STATEMENTS = [

    "CREATE EXTENSION IF NOT EXISTS vector",

    """
    CREATE TABLE IF NOT EXISTS skills (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    )
    """,

    """
    CREATE UNIQUE INDEX IF NOT EXISTS skills_name_unique
    ON skills (LOWER(TRIM(name)))
    """,

    f"""
    CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY,
        external_id TEXT NOT NULL UNIQUE,
        title TEXT,
        company TEXT,
        description TEXT,
        embedding vector({EMBEDDING_DIMENSIONS})
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS job_skills (
        job_id INTEGER NOT NULL
            REFERENCES jobs (id) ON DELETE CASCADE,
        skill_id INTEGER NOT NULL
            REFERENCES skills (id) ON DELETE CASCADE,
        PRIMARY KEY (job_id, skill_id)
    )
    """,

    # The two tables below are only used by the
    # command line helper scripts (candidate_sync.py ...)
    f"""
    CREATE TABLE IF NOT EXISTS candidates (
        id SERIAL PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        embedding vector({EMBEDDING_DIMENSIONS})
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS candidate_skills (
        candidate_id INTEGER NOT NULL
            REFERENCES candidates (id) ON DELETE CASCADE,
        skill_id INTEGER NOT NULL
            REFERENCES skills (id) ON DELETE CASCADE,
        PRIMARY KEY (candidate_id, skill_id)
    )
    """,
]


def create_schema(engine):

    with engine.begin() as connection:

        for statement in SCHEMA_STATEMENTS:

            connection.execute(text(statement))


# ==========================================
# Seed data
# ==========================================

def _load_json(path):

    with open(path, "r", encoding="utf-8") as file:

        return json.load(file)


def sync_job_skills(engine, get_or_create_skill):

    """Link every job to its required skills."""

    jobs = _load_json(JOBS_PATH)

    linked = 0

    with engine.begin() as connection:

        for job in jobs:

            row = connection.execute(
                text("""
                    SELECT id
                    FROM jobs
                    WHERE external_id = :external_id
                """),
                {
                    "external_id":
                        str(job["job_id"])
                }
            ).fetchone()

            if not row:
                continue

            for skill in job.get("required_skills", []):

                if not isinstance(skill, str):
                    continue

                if not skill.strip():
                    continue

                skill_id, _, _ = get_or_create_skill(
                    connection,
                    skill.strip()
                )

                result = connection.execute(
                    text("""
                        INSERT INTO job_skills (
                            job_id,
                            skill_id
                        )
                        VALUES (
                            :job_id,
                            :skill_id
                        )
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "job_id": row.id,
                        "skill_id": skill_id
                    }
                )

                linked += result.rowcount

    return linked


def sync_profile_skills(engine, get_or_create_skill):

    """Add the skills listed in the sample candidate profile
    to the skills table, so they can be found in uploaded CVs."""

    if not CV_PROFILE_PATH.exists():
        return 0

    profile = _load_json(CV_PROFILE_PATH)

    created = 0

    with engine.begin() as connection:

        for skill in profile.get("skills", []):

            if not isinstance(skill, str):
                continue

            if not skill.strip():
                continue

            _, _, was_created = get_or_create_skill(
                connection,
                skill.strip()
            )

            created += int(was_created)

    return created


# ==========================================
# Entry point
# ==========================================

def init_db():

    """Create the schema and load the data if it is missing."""

    # Imported here (not at the top) so that
    # normalize_database_url_env() runs first.
    from src.embedding_model import engine, sync_jobs
    from src.sync_skills import get_or_create_skill

    logger.info("Creating database schema...")

    create_schema(engine)

    logger.info("Loading jobs and embeddings...")

    sync_jobs()

    new_links = sync_job_skills(
        engine,
        get_or_create_skill
    )

    sync_profile_skills(
        engine,
        get_or_create_skill
    )

    with engine.connect() as connection:

        jobs_count = connection.execute(
            text("SELECT COUNT(*) FROM jobs")
        ).scalar()

        skills_count = connection.execute(
            text("SELECT COUNT(*) FROM skills")
        ).scalar()

    logger.info(
        "Database ready: %s jobs, %s skills "
        "(%s new job-skill links)",
        jobs_count,
        skills_count,
        new_links
    )
