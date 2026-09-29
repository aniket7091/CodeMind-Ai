import Sidebar from "../components/Sidebar/Sidebar";
import Header from "../components/Header/Header";
import ChatContainer from "../components/Chat/ChatContainer";
import useChat from "../hooks/useChat";

function ChatPage() {
  const {
    messages,
    loading,
    error,
    sendMessage,
    clearChat,
  } = useChat();

  return (
    <div className="app-layout">
      <Sidebar onNewChat={clearChat} />

      <main className="main-content">
        <Header />

        <ChatContainer
          messages={messages}
          loading={loading}
          error={error}
          onSend={sendMessage}
        />
      </main>
    </div>
  );
}

export default ChatPage;