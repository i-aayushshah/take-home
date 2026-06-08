import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateStatus } from "../api/candidates";
import { toast } from "../store/toastStore";

export function useUpdateStatus(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => updateStatus(candidateId, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
      queryClient.invalidateQueries({ queryKey: ["candidates"] });
      queryClient.invalidateQueries({ queryKey: ["audit", candidateId] });
      const label = variables.status?.replace("_", " ") || "updated";
      toast(`Status set to ${label} — candidate notified by email.`);
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Failed to update status.", "error");
    },
  });
}
