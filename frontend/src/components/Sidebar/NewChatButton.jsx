import './Sidebar.css'

function NewChatButton({ onClick }) {
  return (
    <button className="new-chat-button" onClick={onClick}>
      <span>+</span>
      New Chat
    </button>
  );
}

export default NewChatButton;