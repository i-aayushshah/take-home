import client from "./client";

export async function loginRequest(email, password) {
  const { data } = await client.post("/api/v1/auth/login", { email, password });
  return data;
}

export async function registerRequest(email, password) {
  const { data } = await client.post("/api/v1/auth/register", { email, password });
  return data;
}
