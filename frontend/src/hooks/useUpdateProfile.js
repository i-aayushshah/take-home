import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateProfile } from "../api/candidates";
import { toast } from "../store/toastStore";

export function useUpdateProfile(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => updateProfile(candidateId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
      queryClient.invalidateQueries({ queryKey: ["audit", candidateId] });
      toast("Profile updated from resume parse.");
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Failed to update profile.", "error");
    },
  });
}
