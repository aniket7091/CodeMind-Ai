import './Chat.css'

function LoadingMessage() {
  return (
    <div className="message-row ai-row">
      <div className="ai-avatar">C</div>

      <div className="loading-message">
        <div className="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>

        <p>CodeMind is thinking...</p>
      </div>
    </div>
  );
}

export default LoadingMessage;