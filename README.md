# Semantic Job Matching Tool

An AI-powered job matching system that analyzes a user's resume and recommends relevant job opportunities using semantic similarity, skill matching, and AI evaluation.

## Features

- Upload PDF resume
- Extract resume text and skills
- Generate text embeddings
- Hybrid semantic + skill-based job matching
- AI-powered match evaluation
- Ranked job recommendations
- React frontend + FastAPI backend

## Tech Stack

### Backend
- Python
- FastAPI
- Sentence Transformers
- Scikit-learn
- Google Gemini API
- PostgreSQL

### Frontend
- React
- Vite
- React Router
- CSS

## Project Structure

```text
semantic-search-tool/
├── backend/
│   ├── src/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```
1. Clone the repository
 ```
git clone https://github.com/aqdarahmad/semantic-search-tool.git
cd semantic-search-tool
```
3. Backend
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create a .env file and add your API key:

GEMINI_API_KEY=your_api_key_here

Run the API:
```
uvicorn main:app --reload
```
## Backend:
```
http://127.0.0.1:8000
```
3. Frontend

Open another terminal:
```
cd frontend

npm install

npm run dev
```
## Frontend:
```
http://localhost:5173
```
Usage
- Open the frontend.
- Go to Resume.
- Upload a PDF resume.
- Click Analyze Resume.
- The system extracts skills and returns ranked matching jobs.

This project is currently a work in progress.
