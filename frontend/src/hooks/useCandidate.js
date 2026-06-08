import { useQuery } from "@tanstack/react-query";
import { fetchCandidate } from "../api/candidates";

export function useCandidate(id) {
  return useQuery({
    queryKey: ["candidate", id],
    queryFn: () => fetchCandidate(id),
    enabled: Boolean(id),
    staleTime: 30_000,
  });
}
