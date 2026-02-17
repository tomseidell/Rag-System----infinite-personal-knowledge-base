export class AuthService {
  getAccessToken():string | null {
    return localStorage.getItem("accessToken");
  }
  getRefreshToken():string | null {
    return localStorage.getItem("refreshToken");
  }

  setAccessToken(token: string) {
    localStorage.setItem("accessToken", token);
  }
  setRefreshToken(token: string) {
    localStorage.setItem("refreshToken", token);
  }

  removeTokens(){
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken")
  }
}
