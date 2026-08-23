import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


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
# Calculate Skill Match
# ==========================================

def calculate_skill_match():

    with engine.connect() as connection:

        rows = connection.execute(
            text("""
                SELECT
                    j.id,
                    j.external_id,
                    j.title,
                    j.company,

                    COUNT(js.skill_id) AS total_required_skills,

                    COUNT(
                        CASE
                            WHEN cs.skill_id IS NOT NULL
                            THEN 1
                        END
                    ) AS matched_skills

                FROM jobs j

                JOIN job_skills js
                    ON j.id = js.job_id

                LEFT JOIN candidate_skills cs
                    ON cs.skill_id = js.skill_id
                    AND cs.candidate_id = (
                        SELECT id
                        FROM candidates
                        ORDER BY id
                        LIMIT 1
                    )

                GROUP BY
                    j.id,
                    j.external_id,
                    j.title,
                    j.company

                ORDER BY
                    matched_skills DESC
            """)
        ).fetchall()


    # ======================================
    # Convert Results
    # ======================================

    results = []

    for row in rows:

        total = int(
            row.total_required_skills
        )

        matched = int(
            row.matched_skills
        )

        if total > 0:

            skill_score = (
                matched / total
            )

        else:

            skill_score = 0


        results.append({

            "job_id":
                row.external_id,

            "database_id":
                row.id,

            "title":
                row.title,

            "company":
                row.company,

            "total_required_skills":
                total,

            "matched_skills":
                matched,

            "skill_score":
                skill_score
        })


    return results


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    results = calculate_skill_match()

    print(
        "\n======================================"
    )

    print(
        "          SKILL BASED MATCHING"
    )

    print(
        "======================================\n"
    )


    for rank, job in enumerate(
        results,
        start=1
    ):

        percentage = (
            job["skill_score"] * 100
        )

        print(
            f"{rank}. {job['title']}"
        )

        print(
            f"   Company: {job['company']}"
        )

        print(
            f"   Job ID: {job['job_id']}"
        )

        print(
            f"   Matched Skills: "
            f"{job['matched_skills']}/"
            f"{job['total_required_skills']}"
        )

        print(
            f"   Skill Match: "
            f"{percentage:.2f}%"
        )

        print(
            "--------------------------------------"
        )


    print(
        "\n========== TOP 3 SKILL MATCH ==========\n"
    )

    for rank, job in enumerate(
        results[:3],
        start=1
    ):

        print(
            f"{rank}. "
            f"{job['title']} → "
            f"{job['skill_score'] * 100:.2f}%"
        )