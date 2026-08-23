import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from embedding_model import (
    get_candidate_embedding,
    sync_jobs
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

engine = create_engine(
    DATABASE_URL
)


# ==========================================
# Convert Vector → PostgreSQL format
# ==========================================

def vector_to_pg(vector):

    return "[" + ",".join(
        str(float(x))
        for x in vector
    ) + "]"


# ==========================================
# Calculate Similarity Using pgvector
# ==========================================

def calculate_similarity():

    # --------------------------------------
    # Make sure candidate embedding exists
    # --------------------------------------

    print(
        "\nChecking candidate embedding..."
    )

    candidate_embedding = (
        get_candidate_embedding()
    )

    # --------------------------------------
    # Make sure jobs are synchronized
    # --------------------------------------

    print(
        "\nChecking job embeddings..."
    )

    sync_jobs()

    # --------------------------------------
    # Convert candidate vector
    # --------------------------------------

    candidate_vector = vector_to_pg(
        candidate_embedding
    )

    # --------------------------------------
    # Search using pgvector
    # --------------------------------------

    with engine.connect() as connection:

        rows = connection.execute(
            text("""
                SELECT
                    id,
                    external_id,
                    title,
                    company,
                    description,

                    1 - (
                        embedding <=> CAST(
                            :candidate_embedding
                            AS vector
                        )
                    ) AS similarity_score

                FROM jobs

                WHERE embedding IS NOT NULL

                ORDER BY
                    embedding <=> CAST(
                        :candidate_embedding
                        AS vector
                    )
            """),
            {
                "candidate_embedding":
                    candidate_vector
            }
        ).fetchall()

    # --------------------------------------
    # Convert DB results → dictionaries
    # --------------------------------------

    results = []

    for row in rows:

        results.append({

            "job_id":
                row.external_id,

            "database_id":
                row.id,

            "title":
                row.title,

            "company":
                row.company,

            "description":
                row.description or "",

            "similarity_score":
                float(
                    row.similarity_score
                )
        })

    return results


# ==========================================
# Get Top Jobs
# ==========================================

def get_top_jobs(n=3):

    results = calculate_similarity()

    return results[:n]


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    results = calculate_similarity()

    print(
        "\n======================================"
    )

    print(
        "       CV → JOB SEMANTIC MATCHING"
    )

    print(
        "======================================\n"
    )

    for rank, job in enumerate(
        results,
        start=1
    ):

        percentage = (
            job["similarity_score"] * 100
        )

        print(
            f"{rank}. {job['title']}"
        )

        print(
            f"   Company: "
            f"{job['company']}"
        )

        print(
            f"   Job ID: "
            f"{job['job_id']}"
        )

        print(
            f"   Similarity: "
            f"{percentage:.2f}%"
        )

        print(
            "--------------------------------------"
        )

    # --------------------------------------
    # Top 3
    # --------------------------------------

    print(
        "\n========== TOP 3 ==========\n"
    )

    top_jobs = results[:3]

    for rank, job in enumerate(
        top_jobs,
        start=1
    ):

        print(
            f"{rank}. "
            f"{job['title']} "
            f"→ "
            f"{job['similarity_score'] * 100:.2f}%"
        )