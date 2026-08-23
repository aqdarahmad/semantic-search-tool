import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
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

JOBS_PATH = (
    BASE_DIR
    / "data"
    / "jobs"
    / "jobs.json"
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
# Embedding Model
# ==========================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================================
# JSON Loader
# ==========================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================
# Convert ANY value to text
# ==========================================

def value_to_text(value):

    if isinstance(value, str):
        return value

    if isinstance(value, dict):

        return " | ".join(
            f"{key}: {value_to_text(val)}"
            for key, val in value.items()
        )

    if isinstance(value, list):

        return ", ".join(
            value_to_text(item)
            for item in value
        )

    return str(value)


# ==========================================
# Convert PostgreSQL Vector → NumPy
# ==========================================

def pg_vector_to_numpy(vector):

    # --------------------------------------
    # Already a NumPy array
    # --------------------------------------

    if isinstance(vector, np.ndarray):

        return vector.astype(
            np.float32
        )

    # --------------------------------------
    # PostgreSQL vector returned as string
    # --------------------------------------

    if isinstance(vector, str):

        vector = vector.strip()

        # Remove [ and ]
        if (
            vector.startswith("[")
            and vector.endswith("]")
        ):

            vector = vector[1:-1]

        if not vector:
            raise ValueError(
                "Embedding vector is empty."
            )

        values = [
            float(x.strip())
            for x in vector.split(",")
        ]

        return np.array(
            values,
            dtype=np.float32
        )

    # --------------------------------------
    # List / Tuple
    # --------------------------------------

    if isinstance(
        vector,
        (list, tuple)
    ):

        return np.array(
            vector,
            dtype=np.float32
        )

    # --------------------------------------
    # Unknown format
    # --------------------------------------

    raise TypeError(
        f"Unsupported embedding type: "
        f"{type(vector)}"
    )


# ==========================================
# Candidate → Text
# ==========================================

def candidate_to_text(candidate):

    text_parts = []

    text_parts.append(
        f"Candidate Name: "
        f"{candidate.get('name', '')}"
    )

    # --------------------------------------
    # Skills
    # --------------------------------------

    skills = candidate.get(
        "skills",
        []
    )

    if skills:

        text_parts.append(
            "Skills: "
            + value_to_text(skills)
        )

    # --------------------------------------
    # Experience
    # --------------------------------------

    for experience in candidate.get(
        "experience",
        []
    ):

        text_parts.append(
            f"""
Experience:
Role: {experience.get('role', '')}
Company: {experience.get('company', '')}
Location: {experience.get('location', '')}
Dates: {experience.get('dates', '')}
Description: {value_to_text(
    experience.get('description', [])
)}
"""
        )

    # --------------------------------------
    # Education
    # --------------------------------------

    for education in candidate.get(
        "education",
        []
    ):

        text_parts.append(
            f"""
Education:
Institution: {education.get('institution', '')}
Degree: {education.get('degree', '')}
Location: {education.get('location', '')}
Dates: {education.get('dates', '')}
Grade: {education.get('grade', '')}
"""
        )

    # --------------------------------------
    # Certifications
    # --------------------------------------

    certifications = candidate.get(
        "certifications",
        []
    )

    if certifications:

        text_parts.append(
            "Certifications: "
            + value_to_text(certifications)
        )

    # --------------------------------------
    # Projects
    # --------------------------------------

    for project in candidate.get(
        "projects",
        []
    ):

        if isinstance(project, dict):

            text_parts.append(
                f"""
Project:
Name: {project.get('name', '')}
Technologies: {value_to_text(
    project.get('technologies', [])
)}
Description: {project.get(
    'description',
    ''
)}
"""
            )

        else:

            text_parts.append(
                "Project: "
                + value_to_text(project)
            )

    return "\n".join(text_parts)


# ==========================================
# Job → Text
# ==========================================

def job_to_text(job):

    return f"""
Job Title:
{job.get('title', '')}

Company:
{job.get('company', '')}

Job Description:
{job.get('description', '')}

Required Skills:
{value_to_text(
    job.get('required_skills', [])
)}
"""


# ==========================================
# Convert Vector → PostgreSQL format
# ==========================================

def vector_to_pg(vector):

    return "[" + ",".join(
        str(float(x))
        for x in vector
    ) + "]"


# ==========================================
# Get Candidate Embedding
# ==========================================

def get_candidate_embedding():

    # --------------------------------------
    # Load candidate profile
    # --------------------------------------

    candidate = load_json(
        CV_PROFILE_PATH
    )

    candidate_text = candidate_to_text(
        candidate
    )

    # --------------------------------------
    # Check Database First
    # --------------------------------------

    with engine.connect() as connection:

        result = connection.execute(
            text("""
                SELECT embedding
                FROM candidates
                WHERE embedding IS NOT NULL
                ORDER BY id
                LIMIT 1
            """)
        ).fetchone()

    if result:

        print(
            "Candidate embedding found "
            "in database."
        )

        # IMPORTANT:
        # PostgreSQL vector may be returned
        # as a string.

        return pg_vector_to_numpy(
            result[0]
        )

    # --------------------------------------
    # Generate Embedding
    # --------------------------------------

    print(
        "Candidate embedding not found."
    )

    print(
        "Generating candidate embedding..."
    )

    embedding = model.encode(
        candidate_text,
        normalize_embeddings=True
    )

    embedding = np.array(
        embedding,
        dtype=np.float32
    )

    embedding_string = vector_to_pg(
        embedding
    )

    # --------------------------------------
    # Store Embedding
    # --------------------------------------

    with engine.begin() as connection:

        connection.execute(
            text("""
                UPDATE candidates
                SET embedding =
                    CAST(
                        :embedding
                        AS vector
                    )
                WHERE id = (
                    SELECT id
                    FROM candidates
                    ORDER BY id
                    LIMIT 1
                )
            """),
            {
                "embedding":
                    embedding_string
            }
        )

    print(
        "Candidate embedding saved."
    )

    return embedding

    # ==========================================
# Get Embedding From Text
# ==========================================

def get_text_embedding(text):

    if not text or not text.strip():

        raise ValueError(
            "Text cannot be empty."
        )

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return np.array(
        embedding,
        dtype=np.float32
    )


# ==========================================
# Insert / Update Jobs + Embeddings
# ==========================================

def sync_jobs():

    jobs = load_json(
        JOBS_PATH
    )

    with engine.begin() as connection:

        for job in jobs:

            external_id = job["job_id"]

            # ----------------------------------
            # Check existing job
            # ----------------------------------

            existing = connection.execute(
                text("""
                    SELECT
                        id,
                        embedding
                    FROM jobs
                    WHERE external_id =
                        :external_id
                """),
                {
                    "external_id":
                        external_id
                }
            ).fetchone()

            # ----------------------------------
            # Already exists with embedding
            # ----------------------------------

            if (
                existing
                and existing.embedding is not None
            ):

                print(
                    f"Skipping embedding: "
                    f"{external_id}"
                )

                continue

            # ----------------------------------
            # Generate Job Embedding
            # ----------------------------------

            job_text = job_to_text(
                job
            )

            print(
                f"Creating embedding: "
                f"{external_id}"
            )

            embedding = model.encode(
                job_text,
                normalize_embeddings=True
            )

            embedding = np.array(
                embedding,
                dtype=np.float32
            )

            embedding_string = vector_to_pg(
                embedding
            )

            # ----------------------------------
            # Update Existing Job
            # ----------------------------------

            if existing:

                connection.execute(
                    text("""
                        UPDATE jobs
                        SET
                            title = :title,
                            company = :company,
                            description = :description,
                            embedding =
                                CAST(
                                    :embedding
                                    AS vector
                                )
                        WHERE external_id =
                            :external_id
                    """),
                    {
                        "external_id":
                            external_id,

                        "title":
                            job.get(
                                "title",
                                ""
                            ),

                        "company":
                            job.get(
                                "company",
                                ""
                            ),

                        "description":
                            job.get(
                                "description",
                                ""
                            ),

                        "embedding":
                            embedding_string
                    }
                )

            # ----------------------------------
            # Insert New Job
            # ----------------------------------

            else:

                connection.execute(
                    text("""
                        INSERT INTO jobs (
                            external_id,
                            title,
                            company,
                            description,
                            embedding
                        )
                        VALUES (
                            :external_id,
                            :title,
                            :company,
                            :description,
                            CAST(
                                :embedding
                                AS vector
                            )
                        )
                    """),
                    {
                        "external_id":
                            external_id,

                        "title":
                            job.get(
                                "title",
                                ""
                            ),

                        "company":
                            job.get(
                                "company",
                                ""
                            ),

                        "description":
                            job.get(
                                "description",
                                ""
                            ),

                        "embedding":
                            embedding_string
                    }
                )


# ==========================================
# Get Jobs From Database
# ==========================================

def get_jobs():

    with engine.connect() as connection:

        rows = connection.execute(
            text("""
                SELECT
                    id,
                    external_id,
                    title,
                    company,
                    description,
                    embedding
                FROM jobs
                WHERE embedding IS NOT NULL
                ORDER BY id
            """)
        ).fetchall()

    return rows


# ==========================================
# Create Embeddings
# ==========================================

def create_embeddings():

    print(
        "\nChecking candidate embedding..."
    )

    candidate_embedding = (
        get_candidate_embedding()
    )

    print(
        "\nChecking job embeddings..."
    )

    sync_jobs()

    jobs = get_jobs()

    job_embeddings = np.array([
        pg_vector_to_numpy(
            job.embedding
        )
        for job in jobs
    ])

    return (
        candidate_embedding,
        job_embeddings
    )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    candidate_embedding, job_embeddings = (
        create_embeddings()
    )

    print(
        "\n======================================"
    )

    print(
        "       EMBEDDING DATABASE STATUS"
    )

    print(
        "======================================"
    )

    print(
        "\nCandidate embedding:"
    )

    print(
        candidate_embedding.shape
    )

    print(
        "\nJobs embeddings:"
    )

    print(
        job_embeddings.shape
    )

    print(
        "\nNumber of jobs:"
    )

    print(
        len(job_embeddings)
    )