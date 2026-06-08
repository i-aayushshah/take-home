import { useQuery } from "@tanstack/react-query";
import { fetchTeam } from "../api/auth";

export function useTeam(enabled = true) {
  return useQuery({
    queryKey: ["team"],
    queryFn: fetchTeam,
    enabled,
    staleTime: 60_000,
  });
}
