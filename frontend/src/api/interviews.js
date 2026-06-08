import client from "./client";

export async function fetchCandidateInterviews(candidateId) {
  const { data } = await client.get(`/api/v1/interviews/candidate/${candidateId}`);
  return data;
}

export async function fetchInterviewsInRange(from, to) {
  const { data } = await client.get("/api/v1/interviews", {
    params: { from, to },
  });
  return data;
}

export async function scheduleInterview(candidateId, payload) {
  const { data } = await client.post(`/api/v1/interviews/candidate/${candidateId}`, payload);
  return data;
}

export async function updateInterview(interviewId, payload) {
  const { data } = await client.patch(`/api/v1/interviews/${interviewId}`, payload);
  return data;
}

export async function cancelInterview(interviewId) {
  await client.delete(`/api/v1/interviews/${interviewId}`);
}
