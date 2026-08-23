import { useNavigate } from "react-router-dom";

function Jobs() {
  const navigate = useNavigate();

  return (
    <div className="jobs-page">

      <div className="jobs-empty-state">

        <div className="jobs-empty-icon">
          ✦
        </div>

        <span className="jobs-eyebrow">
          AI JOB MATCHING
        </span>

        <h1>
          Find Your Best Jobs
        </h1>

        <p>
          Upload your resume first to discover jobs
          that match your skills and experience.
        </p>

        <button
          className="upload-resume-btn"
          onClick={() => navigate("/resume")}
        >
          <span>↥</span>
          Upload Resume
        </button>

      </div>

    </div>
  );
}

export default Jobs;