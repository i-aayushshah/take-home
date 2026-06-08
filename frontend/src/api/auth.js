import client from "./client";

export async function loginRequest(email, password) {
  const { data } = await client.post("/api/v1/auth/login", { email, password });
  return data;
}

export async function registerRequest(email, password) {
  const { data } = await client.post("/api/v1/auth/register", { email, password });
  return data;
}

export async function verifyEmailRequest(token) {
  const { data } = await client.get("/api/v1/auth/verify-email", { params: { token } });
  return data;
}

export async function resendVerificationRequest(email) {
  const { data } = await client.post("/api/v1/auth/resend-verification", { email });
  return data;
}

export async function fetchTeam() {
  const { data } = await client.get("/api/v1/auth/team");
  return data;
}
