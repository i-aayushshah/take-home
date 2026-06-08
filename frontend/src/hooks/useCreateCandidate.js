import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createCandidate } from "../api/candidates";
import { toast } from "../store/toastStore";

export function useCreateCandidate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createCandidate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidates"] });
      toast("Candidate created.");
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Failed to create candidate.", "error");
    },
  });
}
