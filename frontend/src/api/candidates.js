import client from "./client";

export async function fetchCandidates(filters) {
  const { data } = await client.get("/api/v1/candidates", { params: filters });
  return data;
}

export async function fetchCandidate(id) {
  const { data } = await client.get(`/api/v1/candidates/${id}`);
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
