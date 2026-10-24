import asyncio
import logging
import os
import threading
import time

from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Request
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Importing "src" loads .env and fixes DATABASE_URL (see src/__init__.py)
from src.bootstrap import init_db

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


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

logger = logging.getLogger("semantic-search")


# ==========================================
# Settings (can be changed with env variables)
# ==========================================

# Maximum size of the uploaded CV
MAX_UPLOAD_MB = int(
    os.getenv("MAX_UPLOAD_MB", "5")
)

MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# Each analysis calls Gemini, so limit them per IP
RATE_LIMIT_REQUESTS = int(
    os.getenv("RATE_LIMIT_REQUESTS", "5")
)

RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv("RATE_LIMIT_WINDOW_SECONDS", "600")
)

# Create the tables and load the jobs on startup
AUTO_INIT_DB = (
    os.getenv("AUTO_INIT_DB", "1") != "0"
)

# Extra frontend origins allowed to call the API
# Example: ALLOWED_ORIGINS=https://my-site.vercel.app
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

EXTRA_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        ""
    ).split(",")
    if origin.strip()
]

# Built frontend (created by the Docker build)
FRONTEND_DIST = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "dist"
)

SERVE_FRONTEND = (
    FRONTEND_DIST / "index.html"
).exists()


# ==========================================
# Startup
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.db_ready = False

    if AUTO_INIT_DB:

        try:

            await asyncio.to_thread(init_db)

            app.state.db_ready = True

        except Exception:

            # Keep the server up so /health works
            # and the real error is visible in the logs
            logger.exception(
                "Database initialization failed"
            )

    else:

        app.state.db_ready = True

    yield


app = FastAPI(
    title="Semantic Job Matching API",
    description="CV to Job Hybrid Matching System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=DEFAULT_ORIGINS + EXTRA_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Simple rate limiter (in memory, per IP)
# Protects the Gemini quota on a public demo
# ==========================================

_request_log = defaultdict(deque)

_request_log_lock = threading.Lock()


def get_client_ip(request: Request):

    forwarded = request.headers.get(
        "x-forwarded-for"
    )

    if forwarded:

        return forwarded.split(",")[0].strip()

    if request.client:

        return request.client.host

    return "unknown"


def check_rate_limit(ip: str):

    now = time.monotonic()

    with _request_log_lock:

        # Remove old entries of every IP so the
        # dictionary does not grow forever
        for key in list(_request_log.keys()):

            timestamps = _request_log[key]

            while (
                timestamps
                and now - timestamps[0]
                > RATE_LIMIT_WINDOW_SECONDS
            ):

                timestamps.popleft()

            if not timestamps and key != ip:

                del _request_log[key]

        timestamps = _request_log[ip]

        if len(timestamps) >= RATE_LIMIT_REQUESTS:

            raise HTTPException(
                status_code=429,
                detail=(
                    "Too many analyses. "
                    "Please wait a few minutes "
                    "and try again."
                )
            )

        timestamps.append(now)


# ==========================================
# Health
# ==========================================

@app.get("/health")
def health(request: Request):

    return {
        "status": "ok",
        "database": (
            "ready"
            if request.app.state.db_ready
            else "error"
        )
    }


# ==========================================
# Matching pipeline
# (blocking work, so it runs in a thread)
# ==========================================

def run_match(contents: bytes, filename: str):

    # ======================================
    # Extract Text
    # ======================================

    try:

        cv_text = extract_cv_text(
            contents,
            filename
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

        logger.exception("Skill extraction failed")

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

        logger.exception("Embedding failed")

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

        logger.exception("Matching failed")

        raise HTTPException(
            status_code=500,
            detail=(
                "Matching failed: "
                f"{str(e)}"
            )
        )

    # ======================================
    # LLM Evaluation
    # The ranked jobs are still useful if Gemini
    # is unavailable (quota, network...), so do
    # not fail the whole request.
    # ======================================

    evaluation = None

    evaluation_error = None

    if results:

        try:

            evaluation = evaluate_matches(
                cv_text,
                candidate_skills,
                results
            )

        except Exception:

            logger.exception("LLM evaluation failed")

            evaluation_error = (
                "AI evaluation is not available "
                "right now."
            )

    return {
        "filename": filename,
        "skills": candidate_skills,
        "count": len(results),
        "results": results,
        "evaluation": evaluation,
        "evaluation_error": evaluation_error
    }


@app.post("/match")
async def match_jobs(
    request: Request,
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
    # Rate limit (after the cheap validation)
    # ======================================

    check_rate_limit(
        get_client_ip(request)
    )

    # ======================================
    # Read CV
    # ======================================

    contents = await file.read(
        MAX_UPLOAD_BYTES + 1
    )

    if not contents:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(contents) > MAX_UPLOAD_BYTES:

        raise HTTPException(
            status_code=413,
            detail=(
                f"File is too large "
                f"(maximum {MAX_UPLOAD_MB} MB)"
            )
        )

    return await asyncio.to_thread(
        run_match,
        contents,
        file.filename
    )


# ==========================================
# Frontend
# If the frontend was built (Docker), the
# backend serves it, so one link is enough.
# Otherwise "/" is a simple status message.
# ==========================================

if SERVE_FRONTEND:

    app.mount(
        "/assets",
        StaticFiles(
            directory=FRONTEND_DIST / "assets"
        ),
        name="assets"
    )

    @app.get(
        "/{full_path:path}",
        include_in_schema=False
    )
    def serve_frontend(full_path: str):

        dist_root = FRONTEND_DIST.resolve()

        candidate = (
            dist_root / full_path
        ).resolve()

        # Files in the dist root (favicon, icons...)
        if (
            full_path
            and candidate.is_file()
            and dist_root in candidate.parents
        ):

            return FileResponse(candidate)

        # Any other path belongs to React Router
        return FileResponse(
            dist_root / "index.html"
        )

else:

    @app.get("/")
    def home():

        return {
            "message":
                "Semantic Job Matching API is running"
        }
