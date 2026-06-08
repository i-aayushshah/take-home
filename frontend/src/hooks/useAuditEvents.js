import { useQuery } from "@tanstack/react-query";
import { fetchAuditEvents } from "../api/candidates";

export function useAuditEvents(candidateId, enabled = true) {
  return useQuery({
    queryKey: ["audit", candidateId],
    queryFn: () => fetchAuditEvents(candidateId),
    enabled: Boolean(candidateId) && enabled,
  });
}
