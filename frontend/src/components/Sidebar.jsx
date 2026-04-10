import { useState } from "react";
import "./Sidebar.css";

export default function Sidebar({ chats, activeChatId, onSelect, onNew, onDelete, onRename, activeTab, onTabChange, onClearReminders }) {
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState("");

  const startEdit = (e, chat) => {
    e.stopPropagation();
    setEditingId(chat.chat_id);
    setEditName(chat.name);
  };

  const submitEdit = (chatId) => {
    if (editName.trim()) onRename(chatId, editName.trim());
    setEditingId(null);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <span style={{fontSize:"22px"}}>🌾</span>
        <span className="logo-text">Celiac AI</span>
      </div>

      <button className="new-chat-btn" onClick={onNew}>
        + New chat
      </button>

      <div className="sidebar-section-label">Conversations</div>

      <div className="chat-list">
        {chats.length === 0 && (
          <p className="no-chats">No chats yet</p>
        )}
        {chats.map(chat => (
          <div
            key={chat.chat_id}
            className={`chat-item ${activeChatId === chat.chat_id ? "active" : ""}`}
            onClick={() => { onSelect(chat.chat_id); onTabChange("chat"); }}
          >
            {editingId === chat.chat_id ? (
              <input
                className="chat-rename-input"
                value={editName}
                onChange={e => setEditName(e.target.value)}
                onBlur={() => submitEdit(chat.chat_id)}
                onKeyDown={e => {
                  if (e.key === "Enter") submitEdit(chat.chat_id);
                  if (e.key === "Escape") setEditingId(null);
                }}
                autoFocus
                onClick={e => e.stopPropagation()}
              />
            ) : (
              <>
                <span className="chat-name">{chat.name || "New chat"}</span>
                <div className="chat-actions">
                  <button
                    title="Rename"
                    onClick={e => startEdit(e, chat)}
                  >✎</button>
                  <button
                    title="Delete"
                    onClick={e => { e.stopPropagation(); onDelete(chat.chat_id); }}
                  >✕</button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>

      <div className="sidebar-bottom">
        <button
          className={`sidebar-tab ${activeTab === "chat" ? "active" : ""}`}
          onClick={() => onTabChange("chat")}
        >
          Chat
        </button>
        <button
          className={`sidebar-tab ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => onTabChange("dashboard")}
        >
          Dashboard
        </button>
        <button
          className="sidebar-tab danger"
          onClick={onClearReminders}
        >Clear reminders</button>
      </div>
    </div>
  );
}