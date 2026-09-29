import { useRef, useEffect } from "react";
import UserMessage from "./UserMessage";
import AIMessage from "./AIMessage";
import LoadingMessage from "./LoadingMessage";
import ChatInput from "./ChatInput";
import ErrorMessage from "../Common/ErrorMessage";
import './Chat.css'

const SUGGESTIONS = [
  "How do I use React hooks?",
  "Explain async/await",
  "Set up a REST API",
  "CSS Grid layout guide",
];

function ChatContainer({
  messages,
  loading,
  error,
  onSend,
}) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading]);

  return (
    <div className="chat-container">
      <div className="messages-area">
        {messages.length === 0 && !loading && (
          <div className="empty-chat">
            <div className="empty-icon">⌘</div>

            <h2>Ask CodeMind</h2>

            <p>
              Ask a coding question and CodeMind will search
              its technical knowledge base to generate a
              grounded answer.
            </p>

            <div className="empty-suggestions">
              {SUGGESTIONS.map((text) => (
                <button
                  className="suggestion-chip"
                  key={text}
                  onClick={() => onSend(text)}
                >
                  {text}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => {
          if (message.role === "user") {
            return (
              <UserMessage
                key={message.id}
                content={message.content}
              />
            );
          }

          return (
            <AIMessage
              key={message.id}
              message={message}
            />
          );
        })}

        {loading && <LoadingMessage />}

        {error && <ErrorMessage message={error} />}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        onSend={onSend}
        loading={loading}
      />
    </div>
  );
}

export default ChatContainer;