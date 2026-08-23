import os
import json

from dotenv import load_dotenv
from google import genai

from cv_parser import extract_text_from_pdf, clean_text


# ==========================================
# Paths
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "cvs",
    "Aqdar Ahmad .pdf"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "candidate_profile.json"
)


# ==========================================
# Gemini Setup
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

client = genai.Client(
    api_key=api_key
)


# ==========================================
# Gemini CV Extraction
# ==========================================

def extract_cv_information(cv_text):

    prompt = f"""
You are an expert CV information extraction system.

Analyze the CV carefully.

Extract ALL relevant information.

IMPORTANT RULES:

1. Do not invent information.
2. Only extract information explicitly present
   in the CV.
3. Extract ALL technical skills mentioned
   anywhere in the CV.
4. Extract ALL certifications.
5. Extract ALL work experiences.
6. Extract ALL education.
7. Extract ALL projects.
8. Preserve original technology names.
9. Do not convert projects into professional experience.
10. Do not convert training into professional experience.
11. Return ONLY valid JSON.

Return exactly:

{{
    "name": "",
    "contact": {{
        "email": "",
        "phone": "",
        "location": ""
    }},
    "skills": [],
    "experience": [],
    "education": [],
    "certifications": [],
    "projects": []
}}

CV:

{cv_text}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# Clean Gemini Response
# ==========================================

def clean_json_response(text):

    text = text.strip()

    text = text.replace(
        "```json",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    return text.strip()


# ==========================================
# Main
# ==========================================

def build_candidate_profile():

    # --------------------------------------
    # Existing profile?
    # --------------------------------------

    if os.path.exists(OUTPUT_PATH):

        print(
            "Candidate profile already exists."
        )

        print(
            "Skipping Gemini CV extraction."
        )

        return


    print(
        "Candidate profile not found."
    )

    print(
        "Extracting CV using Gemini..."
    )


    # --------------------------------------
    # Extract PDF text
    # --------------------------------------

    raw_text = extract_text_from_pdf(
        CV_PATH
    )


    # --------------------------------------
    # Clean CV text
    # --------------------------------------

    clean_cv = clean_text(
        raw_text
    )


    # --------------------------------------
    # Gemini Request
    # --------------------------------------

    result = extract_cv_information(
        clean_cv
    )


    # --------------------------------------
    # Clean JSON
    # --------------------------------------

    result = clean_json_response(
        result
    )


    # --------------------------------------
    # Convert JSON
    # --------------------------------------

    profile = json.loads(
        result
    )


    # --------------------------------------
    # Save profile
    # --------------------------------------

    os.makedirs(
        os.path.dirname(
            OUTPUT_PATH
        ),
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False
        )


    print(
        "Candidate profile saved to:"
    )

    print(
        OUTPUT_PATH
    )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    build_candidate_profile()
    