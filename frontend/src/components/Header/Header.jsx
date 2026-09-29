import './Header.css'

function Header() {
  return (
    <header className="header">
      <div className="header-info">
        <h1>CodeMind AI</h1>
        <p>Developer-focused RAG coding assistant</p>
      </div>

      <div className="backend-status">
        <span className="status-dot"></span>
        Backend Online
      </div>
    </header>
  );
}

export default Header;