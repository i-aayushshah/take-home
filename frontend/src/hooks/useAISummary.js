import { useMutation } from "@tanstack/react-query";
import { triggerSummary } from "../api/candidates";

export function useAISummary(candidateId) {
  return useMutation({
    mutationFn: () => triggerSummary(candidateId),
  });
}
