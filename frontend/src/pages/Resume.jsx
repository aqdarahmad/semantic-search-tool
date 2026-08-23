import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeResume } from "../services/api";

function Resume() {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) return;

    if (selectedFile.type !== "application/pdf") {
      setError("Please upload a PDF file.");
      setFile(null);
      return;
    }

    setError("");
    setFile(selectedFile);
  }

  async function handleAnalyze() {
    if (!file) {
      setError("Please choose your resume first.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await analyzeResume(file);

      localStorage.setItem(
        "resumeMatchResults",
        JSON.stringify(data)
      );

      navigate("/jobs");
    } catch (err) {
      setError(
        err.message || "Failed to analyze your resume."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="resume-page">

      <div className="resume-header">

        <div>
          <span className="resume-eyebrow">
            AI RESUME MATCHING
          </span>

          <h1>
            Find your next opportunity.
          </h1>

          <p>
            Upload your resume and let AI match your
            experience with relevant job opportunities.
          </p>
        </div>

        <div className="resume-header-badge">
          <span>✦</span>
          AI Powered
        </div>

      </div>


      <div className="resume-upload-card">

        <div className="upload-icon">
          ▤
        </div>

        <h2>
          Upload your resume
        </h2>

        <p className="upload-description">
          Add your latest resume in PDF format.
          Our AI will analyze your skills and find
          the most relevant opportunities.
        </p>


        <label
          htmlFor="resume-input"
          className="upload-area"
        >

          <div className="upload-area-icon">
            ↑
          </div>

          <strong>
            {file
              ? file.name
              : "Choose your resume"}
          </strong>

          <span>
            {file
              ? "Resume selected successfully"
              : "Drag & drop your PDF here or click to browse"}
          </span>

          <small>
            PDF files only · Maximum recommended size 10MB
          </small>

        </label>

        <input
          id="resume-input"
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          hidden
        />


        {error && (
          <div className="resume-error">
            {error}
          </div>
        )}


        <button
          className="analyze-resume-btn"
          onClick={handleAnalyze}
          disabled={!file || loading}
        >
          {loading ? (
            <>
              <span className="button-spinner"></span>
              Analyzing Resume...
            </>
          ) : (
            <>
              <span>✦</span>
              Analyze Resume
            </>
          )}
        </button>

      </div>


      <div className="resume-info-grid">

        <div className="resume-info-card">
          <span>01</span>
          <h3>Extract Skills</h3>
          <p>
            AI identifies technical skills,
            experience and relevant keywords.
          </p>
        </div>

        <div className="resume-info-card">
          <span>02</span>
          <h3>Match Jobs</h3>
          <p>
            Your profile is compared with
            available job opportunities.
          </p>
        </div>

        <div className="resume-info-card">
          <span>03</span>
          <h3>Get Your Score</h3>
          <p>
            See which opportunities are the
            strongest matches for you.
          </p>
        </div>

      </div>

    </div>
  );
}

export default Resume;