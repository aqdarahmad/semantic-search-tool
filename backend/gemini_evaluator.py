import os
import json

from dotenv import load_dotenv
from google import genai


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
# Clean Gemini JSON
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
# Evaluate ALL Jobs
# ONE GEMINI REQUEST
# ==========================================

def evaluate_jobs(candidate, jobs):

    prompt = f"""
You are an expert technical recruiter and
AI job matching evaluator.

Evaluate the candidate against ALL provided jobs.

IMPORTANT RULES:

1. Use ONLY information explicitly present
   in the candidate profile.

2. Do NOT invent candidate skills.

3. Do NOT infer a skill from an unrelated
   technology.

4. Do NOT assume Python experience from FastAPI.

5. Do NOT treat projects as professional
   work experience.

6. Do NOT treat training as professional
   work experience.

7. Compare:

   - technical skills
   - professional experience
   - education
   - certifications
   - projects
   - training

8. Matching skills must actually exist
   in the candidate profile.

9. Missing skills must be based on the
   job requirements.

10. Give a realistic match score from
    0 to 100.

11. The score is NOT the probability
    of getting hired.

12. Explain the reasoning using evidence
    from the candidate profile and job.

13. Return one result for EVERY job.

14. Return ONLY valid JSON.

==========================================
CANDIDATE
==========================================

{json.dumps(
    candidate,
    indent=2,
    ensure_ascii=False
)}

==========================================
JOBS
==========================================

{json.dumps(
    jobs,
    indent=2,
    ensure_ascii=False
)}

==========================================
OUTPUT FORMAT
==========================================

Return exactly:

{{
    "ranked_jobs": [
        {{
            "job_id": "",
            "job_title": "",
            "company": "",
            "match_score": 0,
            "decision": "",
            "matching_skills": [],
            "missing_skills": [],
            "relevant_experience": [],
            "strengths": [],
            "weaknesses": [],
            "reason": "",
            "recommendation": ""
        }}
    ]
}}

IMPORTANT:

Return exactly one object for every job.

Do not omit any job.

Sort ranked_jobs from highest
match_score to lowest.
"""


    # ======================================
    # ONLY GEMINI REQUEST IN PIPELINE
    # ======================================

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )


    result = clean_json_response(
        response.text
    )


    return json.loads(
        result
    )