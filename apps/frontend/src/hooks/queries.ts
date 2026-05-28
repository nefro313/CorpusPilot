import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../api/client";
import type { FeedbackRequest } from "../types";

export const queryKeys = {
  documents: ["documents"] as const,
  metrics: ["observability", "summary"] as const,
  anomalies: (threshold: number) => ["observability", "anomalies", threshold] as const,
  feedback: ["observability", "feedback"] as const,
};

export function useDocuments() {
  return useQuery({
    queryKey: queryKeys.documents,
    queryFn: api.listDocuments,
    staleTime: 30_000,
  });
}

export function useMetrics() {
  return useQuery({
    queryKey: queryKeys.metrics,
    queryFn: api.observabilitySummary,
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
}

export function useAnomalies(threshold = 2.5) {
  return useQuery({
    queryKey: queryKeys.anomalies(threshold),
    queryFn: () => api.anomalies(threshold),
    refetchInterval: 60_000,
    staleTime: 30_000,
  });
}

export function useFeedbackSummary() {
  return useQuery({
    queryKey: queryKeys.feedback,
    queryFn: api.feedbackSummary,
    refetchInterval: 60_000,
    staleTime: 30_000,
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.documents });
      queryClient.invalidateQueries({ queryKey: queryKeys.metrics });
    },
  });
}

export function usePostFeedback() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: FeedbackRequest) => api.postFeedback(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.feedback });
    },
  });
}
