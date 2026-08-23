const API_URL = "http://127.0.0.1:8000";

export async function analyzeResume(file) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(`${API_URL}/match`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let message = "Failed to analyze resume";

    try {
      const error = await response.json();
      message = error.detail || message;
    } catch {
      // Ignore invalid error response
    }

    throw new Error(message);
  }

  return await response.json();
}

export async function getJobs() {
  throw new Error(
    "Jobs are loaded after resume analysis. Use analyzeResume()."
  );
}

export async function getJob() {
  throw new Error(
    "Jobs are loaded after resume analysis. Use analyzeResume()."
  );
}