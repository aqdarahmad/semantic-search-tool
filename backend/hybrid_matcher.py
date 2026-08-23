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
# Vector → PostgreSQL
# ==========================================

def vector_to_pg(vector):

    return "[" + ",".join(
        str(float(x))
        for x in vector
    ) + "]"


# ==========================================
# Hybrid Matching
# ==========================================

def calculate_hybrid_matching(
    candidate_embedding,
    candidate_skills
):
    

    candidate_vector = vector_to_pg(
        candidate_embedding
    )

    # --------------------------------------
    # Normalize CV skills
    # --------------------------------------

    candidate_skills = list({
        skill.strip().lower()
        for skill in candidate_skills
        if skill and skill.strip()
    })

    # --------------------------------------
    # Database matching
    # --------------------------------------

    with engine.connect() as connection:

        rows = connection.execute(
            text("""
                SELECT
                    j.id,
                    j.external_id,
                    j.title,
                    j.company,

                    -- Semantic similarity
                    1 - (
                        j.embedding <=> CAST(
                            :candidate_embedding AS vector
                        )
                    ) AS semantic_score,

                    -- Total required skills
                    COUNT(js.skill_id)
                        AS total_required_skills,

                    -- Matched skills
                    COUNT(
                        CASE
                            WHEN LOWER(s.name) = ANY(
                                CAST(
                                    :candidate_skills
                                    AS text[]
                                )
                            )
                            THEN 1
                        END
                    ) AS matched_skills

                FROM jobs j

                JOIN job_skills js
                    ON j.id = js.job_id

                JOIN skills s
                    ON s.id = js.skill_id

                WHERE j.embedding IS NOT NULL

                GROUP BY
                    j.id,
                    j.external_id,
                    j.title,
                    j.company,
                    j.embedding

                ORDER BY semantic_score DESC
            """),
            {
                "candidate_embedding":
                    candidate_vector,

                "candidate_skills":
                    candidate_skills
            }
        ).fetchall()

    # ======================================
    # Build Results
    # ======================================

    results = []

    for row in rows:

        total_skills = int(
            row.total_required_skills
        )

        matched_skills = int(
            row.matched_skills
        )

        # ----------------------------------
        # Skill Score
        # ----------------------------------

        if total_skills > 0:

            skill_score = (
                matched_skills /
                total_skills
            )

        else:

            skill_score = 0.0

        # ----------------------------------
        # Semantic Score
        # ----------------------------------

        semantic_score = float(
            row.semantic_score
        )

        # ----------------------------------
        # Hybrid Score
        # ----------------------------------

        final_score = (
            0.70 * semantic_score
            +
            0.30 * skill_score
        )

        results.append({

            "job_id":
                row.external_id,

            "title":
                row.title,

            "company":
                row.company,

            "semantic_score":
                semantic_score,

            "skill_score":
                skill_score,

            "matched_skills":
                matched_skills,

            "total_skills":
                total_skills,

            "final_score":
                final_score
        })

    # ======================================
    # Sort by Final Score
    # ======================================

    results.sort(
        key=lambda x:
            x["final_score"],
        reverse=True
    )

    return results
