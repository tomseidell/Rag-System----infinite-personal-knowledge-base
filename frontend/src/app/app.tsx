import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Chat } from "../pages/chat/Chat";
import { Login } from "../pages/login/Login";
import { ProtectedRoute } from "components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={
          <ProtectedRoute>
            <Chat />
          </ProtectedRoute>
          } />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
