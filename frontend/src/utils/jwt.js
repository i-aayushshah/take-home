/** Decode a JWT payload without verifying the signature (client display only). */
export function decodeToken(token) {
  const payload = token.split(".")[1];
  const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
  const decoded = JSON.parse(atob(normalized));
  return {
    id: decoded.sub,
    role: decoded.role,
  };
}
