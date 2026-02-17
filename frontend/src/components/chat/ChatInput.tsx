import { Icon } from "@iconify/react";
import { ChatInputProps } from "../../types/props/ChatInputProps";

          
export function ChatInput({value, onChange, onSend, disabled} : ChatInputProps){

    return(
        <div className="flex flex-row p-3 bg-white gap-4 mx-2 mb-2 rounded-xl border border-black/10 shadow-lg hover:shadow-2xl transition-shadow duration-200">
            <input
                className="w-[95%] border-none focus:outline-none focus:ring-0 bg-white"
                placeholder="Ask Anything..."
                value={value}
                onChange={(e) => onChange(e.target.value)}
                >
            </input>
            <button 
            className="bg-black p-2 rounded-lg hover:bg-black/80 transition-colors"
            onClick={onSend}
            disabled={disabled}
            >
                <Icon
                icon="material-symbols:send-outline"
                width="20"
                height="20"
                className="text-white"
                />
            </button>
        </div>
    )
}
          
