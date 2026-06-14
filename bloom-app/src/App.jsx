import { useState, useCallback } from 'react';
import TopBar from './components/TopBar';
import ConfidentialityBanner from './components/ConfidentialityBanner';
import ModuleNav from './components/ModuleNav';
import ChatArea from './components/ChatArea';
import InputBar from './components/InputBar';
import EmployerDashboard from './components/EmployerDashboard';
import { getResponse } from './data/responses';

export default function App() {
  const [view, setView] = useState('employee');
  const [activeModule, setActiveModule] = useState('cycle');
  const [chatHistory, setChatHistory] = useState({
    cycle: [],
    conception: [],
    menopause: [],
    breast: [],
  });
  const [isTyping, setIsTyping] = useState(false);

  const messages = chatHistory[activeModule];

  const handleModuleChange = useCallback((moduleId) => {
    setActiveModule(moduleId);
  }, []);

  const handleSend = useCallback(
    (text) => {
      const userMessage = { role: 'user', text };
      setChatHistory((prev) => ({
        ...prev,
        [activeModule]: [...prev[activeModule], userMessage],
      }));

      setIsTyping(true);

      const delay = 800 + Math.random() * 1200;
      setTimeout(() => {
        const response = getResponse(text);
        const botMessage = {
          role: 'assistant',
          text: response.text,
          source: response.source,
          chips: response.chips,
        };
        setChatHistory((prev) => ({
          ...prev,
          [activeModule]: [...prev[activeModule], botMessage],
        }));
        setIsTyping(false);
      }, delay);
    },
    [activeModule]
  );

  return (
    <div className="app">
      <TopBar view={view} onViewChange={setView} />

      {view === 'employee' ? (
        <>
          <ConfidentialityBanner />
          <ModuleNav activeModule={activeModule} onModuleChange={handleModuleChange} />
          <ChatArea
            messages={messages}
            activeModule={activeModule}
            isTyping={isTyping}
            onStarterClick={handleSend}
          />
          <InputBar onSend={handleSend} disabled={isTyping} />
        </>
      ) : (
        <EmployerDashboard />
      )}
    </div>
  );
}
