import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadResume } from "../api/candidates";
import { toast } from "../store/toastStore";

export function useUploadResume(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file) => uploadResume(candidateId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
      toast("Resume uploaded.");
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Resume upload failed.", "error");
    },
  });
}
