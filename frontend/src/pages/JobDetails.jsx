import { useEffect, useState } from "react";
import {
  useNavigate,
  useParams
} from "react-router-dom";

import { getJob } from "../services/api";

function JobDetails() {

  const { jobId } = useParams();

  const navigate = useNavigate();

  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);


  useEffect(() => {

    async function loadJob() {

      const data = await getJob(jobId);

      setJob(data);

      setLoading(false);

    }

    loadJob();

  }, [jobId]);


  if (loading) {

    return (
      <div className="state-card">
        Loading job...
      </div>
    );

  }


  if (!job) {

    return (
      <div className="state-card">

        <h2>
          Job not found
        </h2>

        <button
          onClick={() =>
            navigate("/jobs")
          }
        >
          Back to Jobs
        </button>

      </div>
    );

  }


  const finalScore =
    Math.round(
      job.final_score * 100
    );

  const semanticScore =
    Math.round(
      job.semantic_score * 100
    );

  const skillScore =
    Math.round(
      job.skill_score * 100
    );


  return (

    <div className="page">

      <button
        className="back-button"
        onClick={() =>
          navigate("/jobs")
        }
      >
        ← Back to jobs
      </button>


      <section className="job-detail-hero">

        <div className="company-logo large">
          {job.company
            ?.charAt(0)
            ?.toUpperCase()}
        </div>

        <div>

          <span className="recommended-tag">
            AI Recommended
          </span>

          <h1>
            {job.title}
          </h1>

          <p>
            {job.company}
          </p>

          <div className="job-detail-meta">
            <span>⌖ Remote</span>
            <span>◷ Full-time</span>
            <span>◉ Junior</span>
          </div>

        </div>

      </section>


      <div className="job-detail-grid">

        <div>

          <section className="detail-section">

            <h2>
              Why you're a match
            </h2>

            <p>
              Our AI analyzed your profile against
              this position and found a strong match
              between your skills and the job
              requirements.
            </p>

          </section>


          <section className="detail-section">

            <h2>
              Job Description
            </h2>

            <p>
              This position is focused on design
              verification and requires strong
              knowledge of digital systems,
              verification methodologies and
              SystemVerilog.
            </p>

          </section>


          <section className="detail-section">

            <h2>
              Required Skills
            </h2>

            <div className="skills">

              <span>SystemVerilog</span>
              <span>UVM</span>
              <span>Verification</span>
              <span>Digital Design</span>
              <span>Computer Architecture</span>

            </div>

          </section>

        </div>


        <aside className="match-summary">

          <span>
            YOUR AI MATCH
          </span>

          <div className="big-score">
            {finalScore}%
          </div>

          <p>
            Excellent compatibility
          </p>


          <div className="score-row">

            <span>
              Semantic Match
            </span>

            <strong>
              {semanticScore}%
            </strong>

          </div>


          <div className="score-row">

            <span>
              Skill Match
            </span>

            <strong>
              {skillScore}%
            </strong>

          </div>


          <div className="score-row">

            <span>
              Skills Matched
            </span>

            <strong>
              {job.matched_skills}/
              {job.total_skills}
            </strong>

          </div>


          <button className="apply-large">
            Apply Now →
          </button>


          <button className="ask-large">
            ✦ Ask Match AI
          </button>

        </aside>

      </div>

    </div>

  );
}

export default JobDetails;