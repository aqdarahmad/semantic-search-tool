import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ==========================================
# Environment
# ==========================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# ==========================================
# Gemini Client
# ==========================================

# Without a timeout, a slow Gemini call would keep the
# request (and the user's spinner) waiting forever.
GEMINI_TIMEOUT_SECONDS = int(
    os.getenv("GEMINI_TIMEOUT_SECONDS", "40")
)

client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        timeout=GEMINI_TIMEOUT_SECONDS * 1000
    )
)


# ==========================================
# Evaluate Matches
# ==========================================

def evaluate_matches(
    cv_text,
    candidate_skills,
    results
):

    # --------------------------------------
    # We only send Top 5 jobs to Gemini
    # --------------------------------------

    top_results = results[:5]

    jobs_text = json.dumps(
        top_results,
        indent=2,
        ensure_ascii=False
    )

    skills_text = ", ".join(
        candidate_skills
    )

    # --------------------------------------
    # Prompt
    # --------------------------------------

    prompt = f"""
You are an expert technical recruiter.

Evaluate how well the candidate matches
the recommended jobs.

Candidate Skills:
{skills_text}

Candidate CV:
{cv_text}

Hybrid Matching Results:
{jobs_text}

For each job, evaluate:

1. Overall suitability
2. Main matching strengths
3. Important missing skills
4. Whether the candidate appears qualified
5. A short recommendation

Do NOT recalculate the hybrid score.

Use the provided semantic_score,
skill_score and final_score as supporting
information.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "evaluations": [
    {{
      "job_id": "string",
      "suitability": "High | Medium | Low",
      "strengths": ["string"],
      "missing_skills": ["string"],
      "qualified": true,
      "recommendation": "string"
    }}
  ],
  "overall_summary": "string"
}}
"""

    # --------------------------------------
    # ONE Gemini Request
    # --------------------------------------

    response = client.models.generate_content(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        ),
        contents=prompt
    )

    # --------------------------------------
    # Parse Response
    # --------------------------------------

    response_text = response.text.strip()

    # Remove markdown code fences if Gemini
    # returns ```json ... ```

    if response_text.startswith("```"):

        response_text = (
            response_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    try:

        evaluation = json.loads(
            response_text
        )

    except json.JSONDecodeError as e:

        raise ValueError(
            "Gemini returned invalid JSON: "
            f"{e}"
        )

    return evaluation