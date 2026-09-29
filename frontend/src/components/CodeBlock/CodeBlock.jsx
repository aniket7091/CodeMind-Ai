import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import './CodeBlock.css'

function CodeBlock({ language, children }) {
  const [copied, setCopied] = useState(false);

  const copyCode = async () => {
    try {
      await navigator.clipboard.writeText(children);
      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 1500);
    } catch (error) {
      console.error("Copy failed:", error);
    }
  };

  return (
    <div className="code-block">
      <div className="code-header">
        <span>{language || "code"}</span>

        <button onClick={copyCode}>
          {copied ? "✓ Copied!" : "Copy"}
        </button>
      </div>

      <SyntaxHighlighter
        language={language || "text"}
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: "16px",
          background: "transparent",
          fontSize: "12.5px",
          lineHeight: "1.7",
        }}
        codeTagProps={{
          style: {
            fontFamily: "'SF Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', monospace",
          },
        }}
      >
        {children}
      </SyntaxHighlighter>
    </div>
  );
}

export default CodeBlock;