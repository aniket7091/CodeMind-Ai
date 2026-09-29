import './Chat.css'

function UserMessage({ content }) {
  return (
    <div className="message-row user-row">
      <div className="user-message">
        <div className="user-message-content">
          {content}
        </div>
      </div>
    </div>
  );
}

export default UserMessage;