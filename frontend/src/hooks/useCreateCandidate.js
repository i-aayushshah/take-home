import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createCandidate } from "../api/candidates";

export function useCreateCandidate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createCandidate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidates"] });
    },
  });
}
