import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./ChatPanel.css";

const AGENT_COLORS = {
  meal_planning:    { bg: "#e8f5e9", color: "#2e7d32", label: "Meal planning" },
  symptom_tracking: { bg: "#fce4ec", color: "#c62828", label: "Symptom tracker" },
  lifestyle:        { bg: "#e3f2fd", color: "#1565c0", label: "Lifestyle coach" },
  reminder:         { bg: "#f3e5f5", color: "#6a1b9a", label: "Reminder agent" },
  general:          { bg: "#f5f5f5", color: "#555",    label: "General" },
};

export default function ChatPanel({ chatId,sessionId, api, onFirstMessage }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
  if (!chatId) return;
  setMessages([]);
  axios.get(`${api}/chats/${chatId}/history`)
    .then(res => {
      if (res.data.length === 0) {
        setMessages([{
          role: "assistant",
          content: "Hi! I'm your celiac disease assistant. I can help with gluten-free meal planning, symptom tracking, lifestyle advice, and setting reminders. What can I help you with today?",
          intent: "general"
        }]);
      } else {
        setMessages(res.data);
      }
    })
    .catch(() => {
      setMessages([{
        role: "assistant",
        content: "Hi! I'm your celiac disease assistant. What can I help you with today?",
        intent: "general"
      }]);
    });
}, [chatId, api]);

  const send = async () => {
    if (!input.trim() || !chatId || loading) return;
    const userMsg = input.trim();
    const isFirst = messages.filter(m => m.role === "user").length === 0; 
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await axios.post(`${api}/chat`, {
        session_id: chatId,
        master_session_id: sessionId,
        message: userMsg
      });
      setMessages(prev => [...prev, {
        role: "assistant",
        content: res.data.response,
        intent: res.data.intent
      }]);
      if (isFirst && onFirstMessage) onFirstMessage(chatId, userMsg);
    } catch {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
        intent: "general"
      }]);
    }
    setLoading(false);
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  const suggestions = [
    "What can I eat for breakfast?",
    "I have bloating after meals",
    "Tips for eating out safely",
    "Remind me to take vitamins daily",
    "What nutrients am I missing?",
  ];

  return (
    <div className="chat-panel">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.role === "assistant" && msg.intent && (
              <div
                className="agent-badge"
                style={{
                  background: AGENT_COLORS[msg.intent]?.bg,
                  color: AGENT_COLORS[msg.intent]?.color
                }}
              >
                {AGENT_COLORS[msg.intent]?.label}
              </div>
            )}
            <div className="bubble">{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="bubble loading">
              <span /><span /><span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length === 1 && (
        <div className="suggestions">
          {suggestions.map((s, i) => (
            <button key={i} className="suggestion" onClick={() => setInput(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      <div className="input-row">
        <textarea
          className="input"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask about celiac disease, meals, symptoms..."
          rows={1}
        />
        <button className="send-btn" onClick={send} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}