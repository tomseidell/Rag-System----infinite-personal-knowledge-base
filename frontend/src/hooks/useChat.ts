import { useMutation } from "@tanstack/react-query";
import { apiClient } from "../lib/apiClient";
import { ChatResponse } from "../types/hooks/ChatResponse";

export function useSendMessage() {
  return useMutation({
    mutationFn: (message: string) =>
      apiClient.post<ChatResponse>("/chat", { message }),
  });
}
