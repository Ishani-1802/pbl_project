import { useState, useEffect } from "react";
import ChatPanel from "./components/ChatPanel";
import Dashboard from "./components/Dashboard";
import ReminderToast from "./components/ReminderToast";
import Sidebar from "./components/Sidebar";
import axios from "axios";
import "./App.css";

const API = "http://localhost:8000";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [activeChatId, setActiveChatId] = useState(null);
  const [chats, setChats] = useState([]);
  const [activeTab, setActiveTab] = useState("chat");
  const [reminders, setReminders] = useState([]);

  useEffect(() => {
    const existing = localStorage.getItem("celiac_session_id");
    if (existing) {
      setSessionId(existing);
      loadChats(existing);
      axios.post(`${API}/activate/${existing}`).catch(() => {});
    } else {
      axios.get(`${API}/session`).then(res => {
        const sid = res.data.session_id;
        localStorage.setItem("celiac_session_id", sid);
        setSessionId(sid);
        loadChats(sid);
        axios.post(`${API}/activate/${sid}`).catch(() => {});
      });
    }
  }, []);

  useEffect(() => {
    if (!sessionId) return;
    const interval = setInterval(() => {
      axios.get(`${API}/reminders/${sessionId}`)
        .then(res => {
          if (res.data.reminders.length > 0)
            setReminders(prev => [...prev, ...res.data.reminders]);
        }).catch(() => {});
    }, 5000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const loadChats = (sid) => {
    axios.get(`${API}/chats/${sid}`).then(res => {
      setChats(res.data);
      if (res.data.length > 0) {
        setActiveChatId(res.data[0].chat_id);
      } else {
        createNewChat(sid);
      }
    }).catch(() => {});
  };

  const createNewChat = (sid) => {
    const s = sid || sessionId;
    axios.post(`${API}/chats/${s}`).then(res => {
      const newChat = { chat_id: res.data.chat_id, name: "New chat" };
      setChats(prev => [newChat, ...prev]);
      setActiveChatId(res.data.chat_id);
    });
  };

  const deleteChat = (chatId) => {
    axios.delete(`${API}/chats/${chatId}`).then(() => {
      const remaining = chats.filter(c => c.chat_id !== chatId);
      setChats(remaining);
      if (activeChatId === chatId) {
        if (remaining.length > 0) setActiveChatId(remaining[0].chat_id);
        else createNewChat();
      }
    });
  };

  const renameChat = (chatId, name) => {
    axios.put(`${API}/chats/${chatId}`, { name }).then(() => {
      setChats(prev => prev.map(c =>
        c.chat_id === chatId ? { ...c, name } : c
      ));
    });
  };

  const dismissReminder = (i) =>
    setReminders(prev => prev.filter((_, idx) => idx !== i));
  const clearReminders = () => {
  if (!sessionId) return;
  axios.delete(`${API}/reminders/${sessionId}`).catch(() => {});
  setReminders([]); // clear toasts immediately
  };

  return (
    <div className="app">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelect={setActiveChatId}
        onNew={() => createNewChat()}
        onDelete={deleteChat}
        onRename={renameChat}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onClearReminders={clearReminders}
      />
      <div className="app-body">
        <main className="main">
          {activeTab === "chat" && activeChatId && (
            <ChatPanel
              key={activeChatId}
              chatId={activeChatId}
              sessionId={sessionId}
              api={API}
              onFirstMessage={(chatId, msg) => renameChat(chatId, msg.slice(0, 30))}
            />
          )}
          {activeTab === "dashboard" && (
            <Dashboard sessionId={sessionId} api={API} />
          )}
        </main>
      </div>

      {reminders.map((msg, i) => (
        <ReminderToast key={i} message={msg} onDismiss={() => dismissReminder(i)} />
      ))}
    </div>
  );
}