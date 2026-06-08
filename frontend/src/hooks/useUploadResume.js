import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadResume } from "../api/candidates";

export function useUploadResume(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file) => uploadResume(candidateId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["candidate", candidateId] });
    },
  });
}
