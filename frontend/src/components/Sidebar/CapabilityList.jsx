import './Sidebar.css'

function CapabilityList() {
  return (
    <div className="capabilities">
      <p className="sidebar-title">Capabilities</p>

      <div className="capability">
        <div className="capability-icon">⌘</div>
        <p>Code Generation</p>
      </div>

      <div className="capability">
        <div className="capability-icon">◈</div>
        <p>Documentation RAG</p>
      </div>

      <div className="capability">
        <div className="capability-icon">◇</div>
        <p>Framework Detection</p>
      </div>

      <div className="capability">
        <div className="capability-icon">✓</div>
        <p>Grounded Answers</p>
      </div>
    </div>
  );
}

export default CapabilityList;