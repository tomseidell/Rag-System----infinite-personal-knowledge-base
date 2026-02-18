import { useMutation } from "@tanstack/react-query";
import { apiClient } from "../lib/apiClient";
import { LoginResponse } from "../types/hooks/LoginResponse";
import { LoginCredentials } from "../types/hooks/LoginCredentials";

export function useLogin() {
  return useMutation({
    mutationFn: (credentials: LoginCredentials) =>
      apiClient.post<LoginResponse>("/user/login", credentials),
  });
}
