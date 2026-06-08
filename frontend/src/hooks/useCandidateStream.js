import { useEffect } from "react";
import useAuthStore from "../store/authStore";
import { getCandidateStreamUrl } from "../api/candidates";

export function useCandidateStream(candidateId, onScore) {
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    if (!candidateId || !token) return undefined;

    const controller = new AbortController();

    async function connect() {
      const response = await fetch(getCandidateStreamUrl(candidateId), {
        headers: { Authorization: `Bearer ${token}` },
        signal: controller.signal,
      });

      if (!response.ok || !response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() || "";

        for (const chunk of chunks) {
          const line = chunk.split("\n").find((item) => item.startsWith("data: "));
          if (!line) continue;
          try {
            const payload = JSON.parse(line.slice(6));
            if (payload.type === "score" && payload.payload) {
              onScore(payload.payload);
            }
          } catch {
            // ignore malformed chunks
          }
        }
      }
    }

    connect().catch(() => {});
    return () => controller.abort();
  }, [candidateId, token, onScore]);
}
