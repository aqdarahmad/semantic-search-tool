// Local development: the backend runs on port 8000.
// Production (Docker/Render): the backend serves the frontend,
// so requests go to the same address ("").
// Set VITE_API_URL to use a different backend.
const API_URL =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

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