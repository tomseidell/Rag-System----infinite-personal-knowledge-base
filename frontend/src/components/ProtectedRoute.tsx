import { Navigate } from "react-router-dom";
import { useAuth } from "hooks/useAuth";

// wrapper for pages
export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAuth();
  
  if (!isLoggedIn) {
    return <Navigate to="/login" />;
  }
  
  // only return children, if user is logged in
  return <>{children}</>;
}
