import { useParams, useNavigate } from "react-router-dom";

function loadResults() {
  try {
    return JSON.parse(
      localStorage.getItem("resumeMatchResults") || "{}"
    );
  } catch {
    return {};
  }
}

function JobDetails() {
  const { jobId } = useParams();
  const navigate = useNavigate();

  // Same key that the Resume page saves the results in
  const data = loadResults();

  const job = data.results?.find(
    (item) => String(item.job_id) === String(jobId)
  );

  // ======================================
  // Find LLM evaluation for this job
  // ======================================

  const evaluation =
    data.evaluation?.evaluations?.find(
      (item) =>
        String(item.job_id) === String(jobId)
    );

  // ======================================
  // Job not found
  // ======================================

  if (!job) {
    return (
      <div className="page">

        <h1>Job Not Found</h1>

        <p>
          This job is no longer available
          in the current matching results.
        </p>

        <button
          onClick={() => navigate("/jobs")}
        >
          Back to Jobs
        </button>

      </div>
    );
  }

  return (
    <div className="page">

      {/* ================================== */}
      {/* Header */}
      {/* ================================== */}

      <button
        className="back-button"
        onClick={() => navigate("/jobs")}
      >
        ← Back to Jobs
      </button>

      <div className="job-details-header">

        <div>

          <span className="eyebrow">
            JOB MATCH
          </span>

          <h1>
            {job.title}
          </h1>

          <p className="company-name">
            {job.company}
          </p>

        </div>

        <div className="match-score-large">

          {Math.round(
            job.final_score * 100
          )}%

          <span>
            Match
          </span>

        </div>

      </div>


      {/* ================================== */}
      {/* Matching Scores */}
      {/* ================================== */}

      <div className="match-stats">

        <div className="stat-card">

          <span>
            Semantic Match
          </span>

          <strong>
            {Math.round(
              job.semantic_score * 100
            )}%
          </strong>

        </div>

        <div className="stat-card">

          <span>
            Skills Match
          </span>

          <strong>
            {Math.round(
              job.skill_score * 100
            )}%
          </strong>

        </div>

        <div className="stat-card">

          <span>
            Skills Matched
          </span>

          <strong>
            {job.matched_skills}/
            {job.total_skills}
          </strong>

        </div>

      </div>


      {/* ================================== */}
      {/* AI Evaluation */}
      {/* ================================== */}

      {evaluation && (

        <div className="ai-evaluation">

          <div className="section-header">

            <span className="eyebrow">
              AI ANALYSIS
            </span>

            <h2>
              AI Job Evaluation
            </h2>

          </div>


          {/* Suitability */}

          <div className="suitability">

            <span>
              Suitability
            </span>

            <strong>
              {evaluation.suitability}
            </strong>

          </div>


          {/* Strengths */}

          {evaluation.strengths?.length > 0 && (

            <div className="evaluation-section">

              <h3>
                ✓ Your Strengths
              </h3>

              <ul>

                {evaluation.strengths.map(
                  (strength, index) => (

                    <li key={index}>
                      {strength}
                    </li>

                  )
                )}

              </ul>

            </div>

          )}


          {/* Missing Skills */}

          {evaluation.missing_skills?.length > 0 && (

            <div className="evaluation-section">

              <h3>
                ⚠ Missing Skills
              </h3>

              <div className="missing-skills">

                {evaluation.missing_skills.map(
                  (skill, index) => (

                    <span
                      key={index}
                      className="skill-tag missing"
                    >
                      {skill}
                    </span>

                  )
                )}

              </div>

            </div>

          )}


          {/* Recommendation */}

          {evaluation.recommendation && (

            <div className="recommendation">

              <h3>
                AI Recommendation
              </h3>

              <p>
                {evaluation.recommendation}
              </p>

            </div>

          )}

        </div>

      )}

    </div>
  );
}

export default JobDetails;