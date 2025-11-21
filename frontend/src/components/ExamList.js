import React, { useEffect, useState } from "react";
import { fetchExamSessions } from "../api";
import { useNavigate } from "react-router-dom";

export default function ExamList() {
  const [sessions, setSessions] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchExamSessions().then((res) => setSessions(res.data));
  }, []);

  return (
    <div className="container">
      <h2>Exam History</h2>
      {sessions.length === 0 && <p>No exams taken yet.</p>}
      <ul>
        {sessions.map((s) => (
          <li
            key={s.uuid}
            style={{ cursor: "pointer", marginBottom: "1rem" }}
            onClick={() => navigate(`/exam/${s.uuid}`)}
          >
            {s.topic.title} - Score: {s.correct}/{s.total} - Finished:{" "}
            {s.finished_at ? new Date(s.finished_at).toLocaleString() : "In Progress"}
          </li>
        ))}
      </ul>
    </div>
  );
}
