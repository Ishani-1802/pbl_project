import { useEffect } from "react";
import "./ReminderToast.css";

export default function ReminderToast({ message, onDismiss }) {
  useEffect(() => {
    const t = setTimeout(onDismiss, 8000);
    return () => clearTimeout(t);
  }, [onDismiss]);

  return (
    <div className="toast">
      <div className="toast-icon">🔔</div>
      <div className="toast-message">{message}</div>
      <button className="toast-close" onClick={onDismiss}>✕</button>
    </div>
  );
}