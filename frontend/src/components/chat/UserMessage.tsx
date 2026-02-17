import { ChatMessage } from "../../types/hooks/ChatMessage";

export function UserMessage({ role, content }: ChatMessage) {
  return (
    <p>
      {content} from {role}
    </p>
  );
}
