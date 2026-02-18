import { useMutation } from "@tanstack/react-query";
import { apiClient } from "../lib/apiClient";

export function useSendMessage() {
  return useMutation({
    mutationFn: (message: string) => apiClient.post("/chat", message),
  });
}
