import { useEffect, useRef } from 'react';
import { BookOpen } from 'lucide-react';
import BloomLogo from './BloomLogo';
import { MODULES } from '../data/modules';

export default function ChatArea({ messages, activeModule, isTyping, onStarterClick }) {
  const endRef = useRef(null);
  const mod = MODULES.find((m) => m.id === activeModule);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (messages.length === 0) {
    return (
      <div className="chat-area">
        <div className="chat-welcome">
          <div className="chat-welcome-icon">
            <BloomLogo size={56} alt="Bloom" />
          </div>
          <h2>{mod.welcome.title}</h2>
          <p>{mod.welcome.description}</p>
          <div className="quick-starters">
            {mod.starters.map((s, i) => (
              <button key={i} className="quick-starter" onClick={() => onStarterClick(s.text)}>
                <span className="quick-starter-icon">{s.icon}</span>
                {s.text}
              </button>
            ))}
          </div>
        </div>
        <div ref={endRef} />
      </div>
    );
  }

  return (
    <div className="chat-area">
      {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.role}`}>
          <div className="message-bubble">
            {msg.text.split('\n').map((line, j) => (
              <p key={j} style={{ marginBottom: j < msg.text.split('\n').length - 1 ? 8 : 0 }}>
                {line.replace(/\*\*(.*?)\*\*/g, '').split(/(\*\*.*?\*\*)/).map((part, k) => {
                  const bold = part.match(/\*\*(.*?)\*\*/);
                  return bold ? <strong key={k}>{bold[1]}</strong> : part;
                })}
              </p>
            ))}
            {msg.source && (
              <div className="message-source">
                <BookOpen size={12} />
                <span>{msg.source}</span>
              </div>
            )}
            {msg.chips && msg.chips.length > 0 && (
              <div className="message-chips">
                {msg.chips.map((chip, j) => (
                  <button key={j} className="chip" onClick={() => onStarterClick(chip)}>
                    {chip}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
      {isTyping && (
        <div className="typing-indicator">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
      )}
      <div ref={endRef} />
    </div>
  );
}
