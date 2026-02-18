const baseUrl = import.meta.env.VITE_BACKEND_URL;

export class AuthService {
  getAccessToken(): string | null {
    return localStorage.getItem("accessToken");
  }
  getRefreshToken(): string | null {
    return localStorage.getItem("refreshToken");
  }

  setAccessToken(token: string) {
    localStorage.setItem("accessToken", token);
  }
  setRefreshToken(token: string) {
    localStorage.setItem("refreshToken", token);
  }

  removeTokens() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  }

  // checks wether access token is still valid or expired
  isAccessTokenValid(): boolean {
    const expiry = localStorage.getItem("accessTokenExpiry");
    if (!expiry) {
      return false;
    }
    return Date.now() < parseInt(expiry);
  }

  async tryRefreshToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    try {
      const res = await fetch(`${baseUrl}/user/refresh`, {
        method: "Post",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        return false;
      }

      const data = await res.json();
      this.setAccessToken(data.accessToken);
      return true;
    } catch {
      return false;
    }
  }
}
