import { useState } from "react";
import { askCodeMind } from "../services/api";

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const sendMessage = async (query) => {
    if (!query.trim() || loading) {
      return;
    }

    setError("");

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const data = await askCodeMind(query);

      const aiMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.answer || "No answer was generated.",
        technology: data.technology,
        framework: data.framework,
        topics: data.topics || [],
        intent: data.intent,
        sources: data.sources || [],
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to CodeMind AI. Make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError("");
  };

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
  };
}