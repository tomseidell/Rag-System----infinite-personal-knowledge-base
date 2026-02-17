import { redirect } from "react-router-dom";
import { AuthService } from "./auth";

const baseUrl = import.meta.env.VITE_BACKEND_URL;

const authService = new AuthService();

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      // add access token as Bearer to request
      Authorization: `Bearer ${authService.getAccessToken()}`,
      ...options?.headers,
    },
  });
  console.log("response", res)

  // if client is unauthorized => access token outdated
  if (res.status == 401) {
    // get new access token with refresh token
    const refreshed = await authService.tryRefreshToken();
    // if valid access token was created, retry request
    if (refreshed) {
      return request(path, options);
    }
    // if no access token could be created, redirect to login page
    authService.removeTokens();
    throw redirect("/login");
  }
  // catch response errors from api 
  if (!res.ok) throw new Error(res.statusText);
  
  return res.json();
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),

  post: <T>(path: string, data: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(data) }),

  patch: <T>(path: string, data: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(data) }),

  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
