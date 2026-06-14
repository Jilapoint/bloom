import { useState } from 'react';
import { Mic, MicOff, Send } from 'lucide-react';

export default function InputBar({ onSend, disabled }) {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);

  function handleSend() {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setText('');
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function toggleRecording() {
    setIsRecording((r) => !r);
    if (!isRecording) {
      setTimeout(() => {
        setIsRecording(false);
        onSend('I have really painful periods — is this normal?');
      }, 2000);
    }
  }

  return (
    <div className="input-bar">
      <button
        className={`input-btn input-btn-voice ${isRecording ? 'recording' : ''}`}
        onClick={toggleRecording}
        aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
      >
        {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
      </button>
      <input
        className="input-field"
        type="text"
        placeholder="Ask Bloom anything..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        aria-label="Message input"
      />
      <button
        className="input-btn input-btn-send"
        onClick={handleSend}
        disabled={!text.trim() || disabled}
        aria-label="Send message"
      >
        <Send size={18} />
      </button>
    </div>
  );
}
