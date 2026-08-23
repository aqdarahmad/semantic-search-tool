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
    raise ValueError("DATABASE_URL not found in .env")


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
# Normalize Skill
# ==========================================

def normalize_skill(skill):

    return " ".join(
        skill.strip().lower().split()
    )


# ==========================================
# Skill Aliases
# ==========================================

SKILL_ALIASES = {

    "system verilog": "SystemVerilog",

    "universal verification methodology (uvm)": "UVM",

    "verisium debugger": "Verdi",

}


# ==========================================
# Get or Create Skill
# ==========================================

def get_or_create_skill(connection, skill_name):

    normalized = normalize_skill(skill_name)

    database_name = SKILL_ALIASES.get(
        normalized,
        skill_name
    )

    # Check existing skill
    row = connection.execute(
        text("""
            SELECT id, name
            FROM skills
            WHERE LOWER(TRIM(name)) = :name
            LIMIT 1
        """),
        {
            "name": normalize_skill(database_name)
        }
    ).fetchone()

    if row:
        return row.id, row.name, False

    # Create new skill
    result = connection.execute(
        text("""
            INSERT INTO skills (name)
            VALUES (:name)
            RETURNING id, name
        """),
        {
            "name": database_name
        }
    ).fetchone()

    return result.id, result.name, True


# ==========================================
# Sync Candidate Skills
# ==========================================

def sync_candidate_skills():

    candidate = load_candidate()

    skills = candidate.get(
        "skills",
        []
    )

    print(
        "\n======================================"
    )

    print(
        "       SYNCING CANDIDATE SKILLS"
    )

    print(
        "======================================"
    )

    print(
        f"Skills found in CV: {len(skills)}"
    )

    with engine.begin() as connection:

        # Get candidate
        candidate_row = connection.execute(
            text("""
                SELECT id, name
                FROM candidates
                ORDER BY id
                LIMIT 1
            """)
        ).fetchone()

        if not candidate_row:

            print(
                "\n❌ No candidate found."
            )

            return

        candidate_id = candidate_row.id

        print(
            f"\nCandidate: {candidate_row.name}"
        )

        print(
            f"Candidate ID: {candidate_id}\n"
        )

        # ----------------------------------
        # Process skills
        # ----------------------------------

        for skill in skills:

            skill_id, skill_name, created = (
                get_or_create_skill(
                    connection,
                    skill
                )
            )

            if created:

                print(
                    f"✓ Created skill: "
                    f"{skill} → {skill_name}"
                )

            else:

                print(
                    f"✓ Existing skill: "
                    f"{skill} → {skill_name}"
                )

            # ----------------------------------
            # Link candidate to skill
            # ----------------------------------

            connection.execute(
                text("""
                    INSERT INTO candidate_skills (
                        candidate_id,
                        skill_id
                    )
                    VALUES (
                        :candidate_id,
                        :skill_id
                    )
                    ON CONFLICT DO NOTHING
                """),
                {
                    "candidate_id": candidate_id,
                    "skill_id": skill_id
                }
            )

    print(
        "\n======================================"
    )

    print(
        "       SKILL SYNC COMPLETE"
    )

    print(
        "======================================"
    )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    sync_candidate_skills()