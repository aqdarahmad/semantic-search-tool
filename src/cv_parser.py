import os
import re

import pymupdf
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


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
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)


# ==========================================
# Extract Text From PDF
# ==========================================

def extract_text_from_pdf(pdf_bytes):

    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text_content = ""

    for page in document:

        text_content += page.get_text()

    document.close()

    return text_content


# ==========================================
# Clean Text
# ==========================================

def clean_text(text_content):

    # Replace bullet points
    text_content = text_content.replace(
        "•",
        " "
    )

    # Replace multiple spaces/tabs
    text_content = re.sub(
        r"[ \t]+",
        " ",
        text_content
    )

    # Remove excessive empty lines
    text_content = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text_content
    )

    # Strip every line
    lines = [
        line.strip()
        for line in text_content.splitlines()
    ]

    # Remove empty lines
    lines = [
        line
        for line in lines
        if line
    ]

    return "\n".join(lines)


# ==========================================
# Extract CV Text
# ==========================================

def extract_cv_text(
    pdf_bytes,
    filename
):

    if not filename.lower().endswith(".pdf"):

        raise ValueError(
            "Only PDF files are supported."
        )

    text_content = extract_text_from_pdf(
        pdf_bytes
    )

    text_content = clean_text(
        text_content
    )

    return text_content


# ==========================================
# Extract Skills
# ==========================================

# ==========================================
# Extract Skills
# ==========================================
def extract_skills(cv_text):

    if not cv_text.strip():
        return []

    with engine.connect() as connection:

        rows = connection.execute(
            text("""
                SELECT name
                FROM skills
                ORDER BY LENGTH(name) DESC
            """)
        ).fetchall()

    database_skills = [
        row[0]
        for row in rows
    ]

    normalized_text = cv_text.lower()

    normalized_text = normalized_text.replace(
        "\n",
        " "
    )

    found_skills = []

    for skill in database_skills:

        skill_clean = skill.strip()

        if not skill_clean:
            continue

        skill_lower = skill_clean.lower()

        pattern = (
            r"(?<!\w)"
            + re.escape(skill_lower)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            normalized_text,
            re.IGNORECASE
        ):

            is_overlapping = False

            for existing_skill in found_skills:

                existing_lower = (
                    existing_skill.lower()
                )

                if (
                    skill_lower in existing_lower
                    or existing_lower in skill_lower
                ):

                    if len(skill_clean) > len(
                        existing_skill
                    ):

                        found_skills.remove(
                            existing_skill
                        )

                    else:

                        is_overlapping = True

                    break

            if not is_overlapping:

                found_skills.append(
                    skill_clean
                )

    return found_skills