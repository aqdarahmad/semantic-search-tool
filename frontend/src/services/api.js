const API_URL = "http://127.0.0.1:8000";

export async function getJobs() {
  const response = await fetch(`${API_URL}/match`);

  if (!response.ok) {
    throw new Error("Failed to fetch jobs");
  }

  const data = await response.json();

  return data.results || [];
}

export async function getJob(id) {
  const jobs = await getJobs();

  return jobs.find(
    (job) => String(job.job_id) === String(id)
  );
}