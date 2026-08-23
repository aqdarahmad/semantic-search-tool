import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getJobs } from "../services/api";

function Jobs() {

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();


  useEffect(() => {

    async function loadJobs() {

      try {

        const data = await getJobs();

        setJobs(data);

      } catch (err) {

        console.error(err);

        setError(
          "Could not connect to the backend."
        );

      } finally {

        setLoading(false);

      }

    }

    loadJobs();

  }, []);


  if (loading) {

    return (
      <div className="state-card">

        <div className="loader"></div>

        <h3>
          Finding your best matches...
        </h3>

      </div>
    );

  }


  if (error) {

    return (
      <div className="state-card">

        <h3>
          Something went wrong
        </h3>

        <p>{error}</p>

      </div>
    );

  }


  return (

    <div className="page">

      <header className="page-header">

        <div>

          <span className="eyebrow">
            AI JOB MATCHING
          </span>

          <h1>
            Find your next opportunity.
          </h1>

          <p>
            Jobs ranked specifically for your
            technical profile.
          </p>

        </div>

        <div className="profile-mini">

          <div className="profile-avatar">
            A
          </div>

          <div>
            <strong>Aqdar</strong>
            <span>Job seeker</span>
          </div>

        </div>

      </header>


      <div className="filters">

        <span>Design Verification</span>
        <span>SystemVerilog</span>
        <span>UVM</span>
        <span>Junior</span>
        <span>Full-time</span>

      </div>


      <div className="results-header">

        <div>

          <h2>
            Recommended for you
          </h2>

          <p>
            {jobs.length} opportunities
            matched by AI
          </p>

        </div>

      </div>


      <div className="jobs-list">

        {jobs.map((job) => (

          <div
            key={job.job_id}
            onClick={() =>
              navigate(
                `/jobs/${job.job_id}`
              )
            }
          >

            <div className="job-card-simple">

              <div className="company-logo">
                {job.company
                  ?.charAt(0)
                  ?.toUpperCase() || "J"}
              </div>

              <div>

                <span className="recommended-tag">
                  AI Recommended
                </span>

                <h3>
                  {job.title}
                </h3>

                <p>
                  {job.company}
                </p>

                <strong>
                  {Math.round(
                    job.final_score * 100
                  )}% Match
                </strong>

              </div>

            </div>

          </div>

        ))}

      </div>

    </div>
  );
}

export default Jobs;