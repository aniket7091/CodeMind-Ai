import './SourceList.css'

function SourceList({ sources }) {
  return (
    <div className="sources">
      <div className="sources-header">
        <span>Sources</span>
        <span>{sources.length}</span>
      </div>

      <div className="source-list">
        {sources.map((source, index) => (
          <div className="source-item" key={index}>
            <div className="source-number">
              {index + 1}
            </div>

            <div className="source-info">
              <strong>{source.source}</strong>

              <span>
                {source.technology}

                {source.framework &&
                  ` · ${source.framework}`}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SourceList;