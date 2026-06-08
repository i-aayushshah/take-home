import { useMutation } from "@tanstack/react-query";
import { parseResume } from "../api/candidates";

export function useParseResume(candidateId) {
  return useMutation({
    mutationFn: () => parseResume(candidateId),
  });
}
