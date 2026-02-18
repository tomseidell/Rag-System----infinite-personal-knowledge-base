import { useAuth } from "hooks/useAuth";
import { useLogin } from "hooks/useLogin";
import { useState } from "react";

export function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();

  const { mutate: submitLogin, isPending, isError } = useLogin();

  const submitLoginForm = () => {
    if (!email || !password) {
      return;
    }

    submitLogin(
      { password, email },
      {
        onSuccess: (data) => {
          login(data.access_token, data.refresh_token);
        },
      },
    );

    setEmail("");
    setPassword("");
  };

  return (
    <div className="flex justify-center items-center self-center ">
      <input
        placeholder="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={() => submitLoginForm()}>Submit</button>
    </div>
  );
}
