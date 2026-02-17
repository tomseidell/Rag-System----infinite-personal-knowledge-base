import { useState } from "react";
import { AuthService } from "../lib/auth";

const authService = new AuthService();

export function useAuth() {
  // state tracking accessToken
  const [isLoggedIn, setIsLoggedIn] = useState(!!authService.getAccessToken());

  // set access token
  const login = (accessToken: string, refreshToken: string) => {
    authService.setAccessToken(accessToken);
    authService.setRefreshToken(refreshToken);
    setIsLoggedIn(true);
  };

  // remove access and refresh token
  const logout = () => {
    authService.removeTokens();
  };

  return { isLoggedIn, login, logout };
}
