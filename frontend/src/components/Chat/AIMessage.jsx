import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CodeBlock from "../CodeBlock/CodeBlock";
import Badge from "../Common/Badge";
import useTypingEffect from "../../hooks/useTypingEffect";
import './Chat.css'

function AIMessage({ message }) {
  const { displayedText, isTyping } = useTypingEffect(message.content);

  return (
    <div className="message-row ai-row">
      <div className="ai-avatar">C</div>

      <div className="message ai-message">
        <div className="message-label">CodeMind AI</div>

        {(message.technology || message.framework) && (
          <div className="message-badges">
            {message.technology && (
              <Badge>{message.technology}</Badge>
            )}

            {message.framework &&
              message.framework !== message.technology && (
                <Badge>{message.framework}</Badge>
              )}
          </div>
        )}

        <div className="markdown-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");

                if (!inline && match) {
                  return (
                    <CodeBlock language={match[1]}>
                      {String(children).replace(/\n$/, "")}
                    </CodeBlock>
                  );
                }

                return (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          >
            {displayedText}
          </ReactMarkdown>
        </div>

        {isTyping && (
          <span className="typing-cursor">|</span>
        )}
        </div>
    </div>
  );
}

export default AIMessage;