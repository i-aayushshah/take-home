import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateNotes } from "../api/candidates";

export function useUpdateNotes(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (internalNotes) => updateNotes(candidateId, internalNotes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
    },
  });
}
