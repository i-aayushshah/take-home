import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateStatus } from "../api/candidates";

export function useUpdateStatus(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => updateStatus(candidateId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
      queryClient.invalidateQueries({ queryKey: ["candidates"] });
    },
  });
}
