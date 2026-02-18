import { ChatInput } from "components/chat/ChatInput";
import { useState } from "react";
import { ChatMessage } from "../../types/hooks/ChatMessage";
import { useSendMessage } from "hooks/useChat";
import { UserMessage } from "components/chat/UserMessage";
import { Header } from "components/chat/Header";

export function Chat() {
  const [textInput, setTextInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const { mutate: sendMessage, isPending, isError } = useSendMessage();

  const handleSend = () => {
    // if input field is empty
    if (!textInput.trim()) {
      return;
    }
    // show message in chat
    setMessages((prev) => [...prev, { role: "user", content: textInput }]);

    //console.log("wird gecalled");
    sendMessage(textInput, {
      onSuccess: (data) => {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.answer },
        ]);
      },
    });

    setTextInput("");
  };

  return (
    <div className="min-h-screen px-10 py-5 flex flex-col bg-[#FAF9F6]">
      {/* Header top right */}
      <Header />

      <div className="mt-2 flex-1 flex justify-center">
        {isError ? <div>Fehler aufgetreten </div> : ""}

        <div className="flex flex-col w-[45%] rounded-xl  content-between justify-between">
          {/* Chat Messages*/}
          <div>
            {messages.map((message) =>
              message.role == "user" ? (
                <UserMessage
                  key={message.content.slice(0, 4)}
                  role={message.role}
                  content={message.content}
                />
              ) : (
                <UserMessage
                  key={message.content.slice(0, 4)}
                  role={"assistant"}
                  content={message.content}
                />
              ),
            )}
          </div>

          {/* Chat input */}
          <ChatInput
            value={textInput}
            onChange={setTextInput}
            onSend={handleSend}
            disabled={isPending}
          />
        </div>
      </div>
    </div>
  );
}
