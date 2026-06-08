import { useMutation, useQueryClient } from "@tanstack/react-query";
import { submitScore } from "../api/candidates";
import { toast } from "../store/toastStore";

export function useSubmitScore(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => submitScore(candidateId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
      toast("Score submitted.");
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Failed to submit score.", "error");
    },
  });
}
