import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  cancelInterview,
  fetchCandidateInterviews,
  fetchInterviewsInRange,
  scheduleInterview,
  updateInterview,
} from "../api/interviews";
import { toast } from "../store/toastStore";

export function useCandidateInterviews(candidateId) {
  return useQuery({
    queryKey: ["interviews", candidateId],
    queryFn: () => fetchCandidateInterviews(candidateId),
    enabled: Boolean(candidateId),
  });
}

export function useInterviewsCalendar(from, to, enabled = true) {
  return useQuery({
    queryKey: ["interviews-calendar", from, to],
    queryFn: () => fetchInterviewsInRange(from, to),
    enabled: Boolean(from) && Boolean(to) && enabled,
  });
}

export function useScheduleInterview(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload) => scheduleInterview(candidateId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interviews", candidateId] });
      queryClient.invalidateQueries({ queryKey: ["interviews-calendar"] });
      queryClient.invalidateQueries({ queryKey: ["audit", candidateId] });
      toast("Interview scheduled — candidate and reviewer notified by email.");
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Failed to schedule interview.", "error");
    },
  });
}

export function useUpdateInterview(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ interviewId, payload }) => updateInterview(interviewId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interviews", candidateId] });
      queryClient.invalidateQueries({ queryKey: ["interviews-calendar"] });
      queryClient.invalidateQueries({ queryKey: ["audit", candidateId] });
      toast("Interview updated — candidate and reviewer notified by email.");
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Failed to update interview.", "error");
    },
  });
}

export function useCancelInterview(candidateId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (interviewId) => cancelInterview(interviewId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["interviews", candidateId] });
      queryClient.invalidateQueries({ queryKey: ["interviews-calendar"] });
      queryClient.invalidateQueries({ queryKey: ["audit", candidateId] });
      toast("Interview cancelled.");
    },
    onError: (error) => {
      toast(error?.response?.data?.detail || "Failed to cancel interview.", "error");
    },
  });
}
