const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function submitApplication(formData) {
  const response = await fetch(`${API_BASE}/api/v1/applications`, {
    method: "POST",
    body: formData,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.detail || "Application failed.");
    error.response = { data };
    throw error;
  }
  return data;
}
