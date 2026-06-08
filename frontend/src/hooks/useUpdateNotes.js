import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateNotes } from "../api/candidates";
import { toast } from "../store/toastStore";

export function useUpdateNotes(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (internalNotes) => updateNotes(candidateId, internalNotes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
      queryClient.invalidateQueries({ queryKey: ["audit", candidateId] });
      toast("Internal notes saved.");
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Failed to save notes.", "error");
    },
  });
}
