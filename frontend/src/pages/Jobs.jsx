import { useState } from "react";
import { useNavigate } from "react-router-dom";

// Results saved by the Resume page (null = no resume analyzed yet)
function loadStoredResults() {
  try {
    const stored =
      localStorage.getItem("resumeMatchResults");

    return stored ? JSON.parse(stored) : null;
  } catch (error) {
    console.error(
      "Failed to load matching results:",
      error
    );

    return null;
  }
}

function Jobs() {
  const navigate = useNavigate();

  const [stored] = useState(loadStoredResults);

  const hasAnalyzed = stored !== null;

  const results = stored?.results || [];
  const candidateSkills = stored?.skills || [];

  function formatScore(score) {
    if (score === undefined || score === null) {
      return 0;
    }

    return Math.round(Number(score) * 100);
  }

  return (
    <div className="jobs-page">

      {/* Header */}

      <div className="jobs-header">

        <div>

          <span className="jobs-eyebrow">
            AI JOB MATCHING
          </span>

          <h1>
            Your Best Job Matches
          </h1>

          <p>
            Opportunities ranked using semantic similarity
            and skill matching.
          </p>

        </div>

        <button
          className="upload-resume-btn"
          onClick={() => navigate("/resume")}
        >
          <span>↥</span>
          {hasAnalyzed
            ? "Analyze Another Resume"
            : "Upload Your Resume"}
        </button>

      </div>


      {/* Candidate Skills */}

      {candidateSkills.length > 0 && (

        <div className="candidate-skills-section">

          <div>

            <span className="section-label">
              YOUR SKILLS
            </span>

            <h2>
              Skills detected from your resume
            </h2>

          </div>

          <div className="candidate-skills">

            {candidateSkills.map(
              (skill, index) => (

                <span
                  className="candidate-skill"
                  key={index}
                >
                  {skill}
                </span>

              )
            )}

          </div>

        </div>

      )}


      {/* Results */}

      <div className="jobs-results">

        {hasAnalyzed && (

          <div className="jobs-results-header">

            <span>
              {results.length} matching opportunities
            </span>

          </div>

        )}


        {!hasAnalyzed ? (

          <div className="jobs-empty-state">

            <div className="jobs-empty-icon">
              ↥
            </div>

            <span className="jobs-eyebrow">
              GET STARTED
            </span>

            <h1>
              Upload your resume to see your matches
            </h1>

            <p>
              Upload a PDF resume and the AI will extract
              your skills and rank the jobs that fit you best.
            </p>

            <button
              className="upload-resume-btn"
              onClick={() => navigate("/resume")}
            >
              <span>↥</span>
              Upload Your Resume
            </button>

          </div>

        ) : results.length === 0 ? (

          <div className="jobs-empty-state">

            <div className="jobs-empty-icon">
              ✦
            </div>

            <span className="jobs-eyebrow">
              NO RESULTS
            </span>

            <h1>
              No job matches found
            </h1>

            <p>
              Try uploading another resume with more
              detailed skills and experience.
            </p>

            <button
              className="upload-resume-btn"
              onClick={() => navigate("/resume")}
            >
              <span>↥</span>
              Try Another Resume
            </button>

          </div>

        ) : (

          <div className="jobs-grid">

            {results.map((job, index) => {

              const finalScore =
                formatScore(job.final_score);

              const semanticScore =
                formatScore(job.semantic_score);

              const skillScore =
                formatScore(job.skill_score);

              return (

                <div
                  className="job-card"
                  key={job.job_id || index}
                >

                  {/* Card Header */}

                  <div className="job-card-top">

                    <div className="job-number">
                      #{index + 1}
                    </div>

                    <div className="match-score">

                      <strong>
                        {finalScore}%
                      </strong>

                      <span>
                        Match
                      </span>

                    </div>

                  </div>


                  {/* Job Info */}

                  <h2 className="job-title">
                    {job.title}
                  </h2>

                  <p className="job-company">
                    {job.company}
                  </p>


                  {/* Score */}

                  <div className="score-section">

                    <div className="score-row">

                      <span>
                        Semantic Match
                      </span>

                      <strong>
                        {semanticScore}%
                      </strong>

                    </div>

                    <div className="score-bar">

                      <div
                        className="score-fill"
                        style={{
                          width: `${semanticScore}%`
                        }}
                      />

                    </div>


                    <div className="score-row">

                      <span>
                        Skill Match
                      </span>

                      <strong>
                        {skillScore}%
                      </strong>

                    </div>

                    <div className="score-bar">

                      <div
                        className="score-fill"
                        style={{
                          width: `${skillScore}%`
                        }}
                      />

                    </div>

                  </div>


                  {/* Skills */}

                  <div className="skills-match">

                    <span className="skills-match-label">
                      Skills Match
                    </span>

                    <div className="skills-count">

                      <strong>
                        {job.matched_skills}
                      </strong>

                      <span>
                        / {job.total_skills} required
                      </span>

                    </div>

                  </div>


                  {/* Footer */}

                  <button
                    className="job-view-btn"
                    onClick={() => {

                      if (job.job_id) {

                        window.open(
                          `https://www.google.com/search?q=${encodeURIComponent(
                            `${job.title} ${job.company}`
                          )}`,
                          "_blank",
                          "noopener,noreferrer"
                        );

                      }

                    }}
                  >
                    Search Opportunity
                    <span>→</span>
                  </button>

                </div>

              );

            })}

          </div>

        )}

      </div>

    </div>
  );
}

export default Jobs;