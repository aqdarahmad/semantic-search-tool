from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from src.cv_parser import (
    extract_cv_text,
    extract_skills
)

from src.embedding_model import (
    get_text_embedding
)

from src.hybrid_matcher import (
    calculate_hybrid_matching
)
from src.evaluator import evaluate_matches

app = FastAPI(
    title="Semantic Job Matching API",
    description="CV to Job Hybrid Matching System",
    version="1.0.0"
)


@app.get("/")
def home():

    return {
        "message":
            "Semantic Job Matching API is running"
    }


@app.post("/match")
async def match_jobs(
    file: UploadFile = File(...)
):

    # ======================================
    # Validate File
    # ======================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file uploaded"
        )

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # ======================================
    # Read CV
    # ======================================

    contents = await file.read()

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # ======================================
    # Extract Text
    # ======================================

    try:

        cv_text = extract_cv_text(
            contents,
            file.filename
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=f"Could not read CV: {str(e)}"
        )

    if not cv_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from CV"
        )

    # ======================================
    # Extract Skills
    # ======================================

    try:

        candidate_skills = extract_skills(
            cv_text
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not extract skills: {str(e)}"
        )

    # ======================================
    # Generate CV Embedding
    # ======================================

    try:

        candidate_embedding = get_text_embedding(
            cv_text
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not generate CV embedding: "
                f"{str(e)}"
            )
        )

    # ======================================
    # Hybrid Matching
    # ======================================

    try:

        results = calculate_hybrid_matching(
            candidate_embedding,
            candidate_skills
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Matching failed: "
                f"{str(e)}"
            )
        )

    # ======================================
    # LLM Evaluation
    # ======================================

    try:

        evaluation = evaluate_matches(
            cv_text,
            candidate_skills,
            results
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "LLM evaluation failed: "
                f"{str(e)}"
            )
        )

    # ======================================
    # Response
    # ======================================

    return {
        "filename": file.filename,
        "skills": candidate_skills,
        "count": len(results),
        "results": results,
        "evaluation": evaluation
    }