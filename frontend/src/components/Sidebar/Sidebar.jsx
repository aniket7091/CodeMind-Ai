import NewChatButton from "./NewChatButton";
import CapabilityList from "./CapabilityList";
import './Sidebar.css'

function Sidebar({ onNewChat }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-box">C</div>

        <div>
          <h2>CodeMind</h2>
          <span>AI Developer Assistant</span>
        </div>
      </div>

      <NewChatButton onClick={onNewChat} />

      <CapabilityList />

      <div className="sidebar-footer">
        <span>CodeMind AI</span>
        <span>v1.0</span>
      </div>
    </aside>
  );
}

export default Sidebar;