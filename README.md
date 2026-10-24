# Semantic Job Matching Tool

An AI-powered job matching system that analyzes a user's resume and recommends relevant job opportunities using semantic similarity, skill matching, and AI evaluation.

## Features

- Upload PDF resume
- Extract resume text and skills
- Generate text embeddings (all-MiniLM-L6-v2 on ONNX Runtime, no PyTorch)
- Hybrid semantic + skill-based job matching (pgvector)
- AI-powered match evaluation (Google Gemini)
- Ranked job recommendations
- React frontend + FastAPI backend, served from one link
- Creates its own database tables and loads the jobs on first start

## Tech Stack

### Backend
- Python
- FastAPI
- fastembed (ONNX Runtime) with all-MiniLM-L6-v2
- Google Gemini API
- PostgreSQL + pgvector
- SQLAlchemy + psycopg 3

### Frontend
- React
- Vite
- React Router
- CSS

## Project Structure

```text
semantic-search-tool/
├── src/
│   ├── main.py             # FastAPI app (API, rate limit, serves the frontend)
│   ├── bootstrap.py        # creates the tables and loads jobs + skills
│   ├── cv_parser.py        # PDF text + skill extraction
│   ├── embedding_model.py  # embeddings (ONNX) and database helpers
│   ├── hybrid_matcher.py   # semantic + skill score
│   └── evaluator.py        # Gemini evaluation of the top jobs
├── data/
│   ├── jobs/jobs.json      # the jobs that are matched against
│   └── processed/          # sample candidate profile
├── frontend/               # React + Vite app
├── Dockerfile
├── render.yaml
├── requirements.txt
└── .env.example
```

## Run locally

You need Python 3.13, Node 22 and a PostgreSQL database with the
[pgvector](https://github.com/pgvector/pgvector) extension
(the easiest option is a free [Neon](https://neon.tech) database).

```bash
git clone https://github.com/aqdarahmad/semantic-search-tool.git
cd semantic-search-tool

python -m venv venv
venv\Scripts\activate          # Linux / macOS: source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your values:

```env
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
GEMINI_API_KEY=your_gemini_api_key
```

Start the backend from the project root (the tables are created and the jobs are loaded automatically on startup):

```bash
uvicorn src.main:app --reload
```

Backend: http://127.0.0.1:8000 (interactive docs at `/docs`)

In another terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Usage

- Open the frontend.
- Go to Resume.
- Upload a PDF resume.
- Click Analyze Resume.
- The system extracts skills and returns ranked matching jobs.

<img width="1860" height="909" alt="image" src="https://github.com/user-attachments/assets/dc8c1886-cc7f-48c0-af64-4a04c051ede0" />

<img width="1883" height="905" alt="image" src="https://github.com/user-attachments/assets/bb258bf3-caed-4468-8d69-b517e8973b12" />
<img width="1889" height="915" alt="image" src="https://github.com/user-attachments/assets/cba78d3c-265d-47b5-b61a-10a0ff9be08b" />
<img width="1877" height="908" alt="image" src="https://github.com/user-attachments/assets/cd29d1c9-d035-4f91-a130-b7d1132ce832" />

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check (`{"status": "ok", "database": "ready"}`) |
| `POST` | `/match` | Upload a PDF (`file` form field) and get ranked jobs |

`POST /match` status codes: `200` ok, `400` invalid file, `413` file too large, `429` rate limit reached, `500` processing error.
If Gemini is unavailable, the ranked jobs are still returned with `evaluation: null`.

## Deploy on Render (free)

The `Dockerfile` builds the React frontend and the Python backend into one image, so the whole app is on **one link**.

### 1. Create the database (Neon)

1. Create a free project on https://neon.tech.
2. Copy the **connection string** (it looks like `postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require`).

You do not need to create any table: the app creates them (and enables `pgvector`) on its first start.

### 2. Create the web service (Render)

1. On https://render.com choose **New +** → **Web Service** and select this repository
   (or **New +** → **Blueprint**, which reads `render.yaml`).
2. Runtime: **Docker**. Instance type: **Free**. Health check path: `/health`.
3. Add the environment variables:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | the Neon connection string |
| `GEMINI_API_KEY` | your Gemini API key |

4. Deploy. Your app is live at `https://<your-service>.onrender.com`.

Things to know about the free plan: the service sleeps after about 15 minutes without visitors (the first request afterwards takes around a minute) and it has 512 MB of RAM, which this lightweight version is built to fit.

### Optional environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Gemini model used for the evaluation |
| `RATE_LIMIT_REQUESTS` | `5` | Analyses allowed per IP in the time window |
| `RATE_LIMIT_WINDOW_SECONDS` | `600` | Length of the rate-limit window |
| `MAX_UPLOAD_MB` | `5` | Maximum size of the uploaded PDF |
| `ALLOWED_ORIGINS` | empty | Extra frontend URLs allowed by CORS (only if the frontend is hosted elsewhere) |
| `AUTO_INIT_DB` | `1` | Set to `0` to skip creating the tables on startup |
| `LOG_LEVEL` | `INFO` | Logging level |

The rate limit protects your Gemini quota on a public link.

## Notes

This project is currently a work in progress.
