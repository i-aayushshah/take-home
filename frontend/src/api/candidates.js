import client from "./client";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function fetchCandidates(filters) {
  const { data } = await client.get("/api/v1/candidates", { params: filters });
  return data;
}

export async function fetchCandidate(id) {
  const { data } = await client.get(`/api/v1/candidates/${id}`);
  return data;
}

export async function createCandidate(payload) {
  const { data } = await client.post("/api/v1/candidates", payload);
  return data;
}

export async function submitScore(id, payload) {
  const { data } = await client.post(`/api/v1/candidates/${id}/scores`, payload);
  return data;
}

export async function triggerSummary(id) {
  const { data } = await client.post(`/api/v1/candidates/${id}/summary`);
  return data;
}

export async function updateNotes(id, internalNotes) {
  const { data } = await client.patch(`/api/v1/candidates/${id}/notes`, {
    internal_notes: internalNotes,
  });
  return data;
}

export async function updateStatus(id, payload) {
  const { data } = await client.patch(`/api/v1/candidates/${id}/status`, payload);
  return data;
}

export async function uploadResume(id, file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await client.post(`/api/v1/candidates/${id}/resume`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function deleteCandidate(id) {
  await client.delete(`/api/v1/candidates/${id}`);
}

export async function downloadResume(id) {
  const response = await client.get(`/api/v1/candidates/${id}/resume`, {
    responseType: "blob",
  });
  return response;
}

export function getCandidateStreamUrl(id) {
  return `${API_BASE}/api/v1/candidates/${id}/stream`;
}

export async function fetchAuditEvents(id) {
  const { data } = await client.get(`/api/v1/candidates/${id}/audit`);
  return data;
}

export async function parseResume(id) {
  const { data } = await client.post(`/api/v1/candidates/${id}/parse-resume`);
  return data;
}

export async function updateProfile(id, payload) {
  const { data } = await client.patch(`/api/v1/candidates/${id}/profile`, payload);
  return data;
}
