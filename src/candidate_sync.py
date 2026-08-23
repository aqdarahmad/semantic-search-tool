import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ==========================================
# Paths
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

CV_PROFILE_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "candidate_profile.json"
)


# ==========================================
# Environment
# ==========================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in .env"
    )


# ==========================================
# Database
# ==========================================

engine = create_engine(DATABASE_URL)


# ==========================================
# Load Candidate
# ==========================================

def load_candidate():

    with open(
        CV_PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================
# Insert Candidate
# ==========================================

def sync_candidate():

    candidate = load_candidate()

    name = candidate.get(
        "name",
        ""
    )

    email = candidate.get(
        "email",
        ""
    )

    phone = candidate.get(
        "phone",
        ""
    )

    location = candidate.get(
        "location",
        ""
    )

    print(
        "\n======================================"
    )

    print(
        "       SYNCING CANDIDATE"
    )

    print(
        "======================================"
    )

    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print(f"Location: {location}")

    with engine.begin() as connection:

        # ----------------------------------
        # Check if candidate already exists
        # ----------------------------------

        existing = connection.execute(
            text("""
                SELECT id
                FROM candidates
                WHERE email = :email
                LIMIT 1
            """),
            {
                "email": email
            }
        ).fetchone()

        # ----------------------------------
        # Already exists
        # ----------------------------------

        if existing:

            print(
                f"\nCandidate already exists."
            )

            print(
                f"Candidate ID: {existing.id}"
            )

            return

        # ----------------------------------
        # Insert Candidate
        # ----------------------------------

        result = connection.execute(
            text("""
                INSERT INTO candidates (
                    name,
                    email,
                    phone,
                    location
                )
                VALUES (
                    :name,
                    :email,
                    :phone,
                    :location
                )
                RETURNING id
            """),
            {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location
            }
        )

        candidate_id = result.scalar()

        print(
            f"\nCandidate inserted successfully!"
        )

        print(
            f"Candidate ID: {candidate_id}"
        )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    sync_candidate()