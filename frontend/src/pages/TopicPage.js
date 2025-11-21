import React, { useState, useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchExamSessionsByTopic } from "../api";

export default function TopicPage() {
  const { id } = useParams();
  const [sessions, setSessions] = useState([]);
  const [topic, setTopic] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getSessions = async () => {
      try {
        const response = await fetchExamSessionsByTopic(id);
        setSessions(response.data);
        if (response.data.length > 0) {
          setTopic(response.data[0].topic);
        }
      } catch (error) {
        setError("Error fetching exam sessions.");
        console.error("Error fetching exam sessions:", error);
      }
    };

    getSessions();
  }, [id]);

  const handleSessionClick = (session) => {
    window.location.href = `/session/${session.uuid}`;
  };

  if (error) {
    return <div className="container">{error}</div>;
  }

  return (
    <div className="container">
      <h1>Topic: {topic ? topic.title : `Topic #${id}`}</h1>

      <Link to={`/topic/${id}/quiz`}>
        <button className="btn">Start New Quiz</button>
      </Link>

      <h2>Past Exam Sessions</h2>
      {sessions.length > 0 ? (
        <ul className="session-list">
          {sessions.map((session) => (
            <li key={session.uuid} onClick={() => handleSessionClick(session)}>
              <div className="session-item">
                <p>Date: {new Date(session.finished_at).toLocaleString()}</p>
                <p>
                  Score: {session.correct_count} / {session.question_order.length}
                </p>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p>No past exam sessions found for this topic.</p>
      )}
    </div>
  );
}
