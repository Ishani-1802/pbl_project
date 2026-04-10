import { useEffect, useState } from "react";
import axios from "axios";
import "./Dashboard.css";

export default function Dashboard({ sessionId, api }) {
  const [symptoms, setSymptoms] = useState([]);
  const [meals, setMeals] = useState([]);

  useEffect(() => {
    if (!sessionId) return;
    axios.get(`${api}/symptoms/${sessionId}`).then(res => setSymptoms(res.data)).catch(() => {});
    axios.get(`${api}/meals/${sessionId}`).then(res => setMeals(res.data)).catch(() => {});
  }, [sessionId, api]);

  const exportPDF = () => {
    window.open(`${api}/export/${sessionId}`, "_blank");
  };

  const grouped = symptoms.reduce((acc, s) => {
    acc[s.symptom] = (acc[s.symptom] || 0) + 1;
    return acc;
  }, {});

  const tips = [
    "Always check labels for hidden gluten in sauces and seasonings",
    "Use separate cookware to avoid cross-contamination",
    "Common deficiencies: Vitamin D, B12, Iron, Folate",
    "Stress can worsen celiac symptoms — try daily relaxation",
    "Oats are only safe if certified gluten-free",
    "When eating out, ask about dedicated fryers and prep areas",
  ];

  return (
    <div className="dashboard">
      <div className="dash-header">
        <h2>Your health dashboard</h2>
        <button className="export-btn" onClick={exportPDF}>
          Download PDF report
        </button>
      </div>

      <div className="dash-grid">
        <div className="card">
          <h2>Symptom log</h2>
          {symptoms.length === 0 ? (
            <p className="empty">No symptoms logged yet. Tell the chatbot about any symptoms you're experiencing.</p>
          ) : (
            <div className="symptom-list">
              {Object.entries(grouped).map(([symptom, count]) => (
                <div key={symptom} className="symptom-row">
                  <span className="symptom-name">{symptom}</span>
                  <div className="symptom-bar">
                    <div className="symptom-fill" style={{ width: `${Math.min(count * 20, 100)}%` }} />
                  </div>
                  <span className="symptom-count">{count}x</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h2>Quick tips</h2>
          <ul className="tips-list">
            {tips.map((tip, i) => <li key={i}>{tip}</li>)}
          </ul>
        </div>

        <div className="card full-width">
          <h2>Meal log</h2>
          {meals.length === 0 ? (
            <p className="empty">No meals logged yet. Tell the chatbot what you ate and it will track it automatically.</p>
          ) : (
            <table className="symptom-table">
              <thead><tr><th>Meal</th><th>Time</th></tr></thead>
              <tbody>
                {meals.slice(0, 15).map((m, i) => (
                  <tr key={i}>
                    <td>{m.meal}</td>
                    <td>{new Date(m.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card full-width">
          <h2>Symptom history</h2>
          {symptoms.length === 0 ? (
            <p className="empty">No history yet.</p>
          ) : (
            <table className="symptom-table">
              <thead><tr><th>Symptom</th><th>Severity</th><th>Time</th></tr></thead>
              <tbody>
                {symptoms.slice(0, 10).map((s, i) => (
                  <tr key={i}>
                    <td>{s.symptom}</td>
                    <td>{s.severity}/10</td>
                    <td>{new Date(s.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}