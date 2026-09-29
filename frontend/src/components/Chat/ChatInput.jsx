import { useState } from "react";
import './Chat.css'

function ChatInput({ onSend, loading }) {
  const [input, setInput] = useState("");

  const submit = () => {
    if (!input.trim() || loading) {
      return;
    }

    onSend(input);
    setInput("");
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <div className="chat-input-area">
      <div className="chat-input-wrapper">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask CodeMind anything about coding..."
          rows={1}
          disabled={loading}
        />

        <button
          className="send-button"
          onClick={submit}
          disabled={!input.trim() || loading}
          aria-label="Send message"
        >
          {loading ? "⋯" : "↑"}
        </button>
      </div>

      <div className="input-footer">
        <span>
          Press <kbd>Enter</kbd> to send · <kbd>Shift + Enter</kbd> for new line
        </span>
      </div>
    </div>
  );
}

export default ChatInput;