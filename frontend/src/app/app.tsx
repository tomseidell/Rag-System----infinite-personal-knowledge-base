import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Chat } from "../pages/chat/Chat";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Chat />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
