import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchExamSessionDetail } from "../api";

export default function ExamDetail() {
  const { uuid } = useParams();
  const [session, setSession] = useState(null);

  useEffect(() => {
    fetchExamSessionDetail(uuid).then((res) => setSession(res.data));
  }, [uuid]);

  if (!session) return <p>Loading...</p>;

  return (
    <div className="container">
      <h2>{session.topic.title} - Exam Details</h2>
      <p>
        Finished: {session.finished_at ? new Date(session.finished_at).toLocaleString() : "In Progress"}
      </p>
      <p>Correct: {session.correct}, Wrong: {session.wrong}, Unattempted: {session.unattempted}</p>

      <h3>Questions</h3>
      {session.details.map((q) => (
        <div key={q.question_id} className="result-question">
          <p><strong>Q:</strong> {q.question}</p>
          <p><strong>Your Answer:</strong> {q.chosen_index !== null && q.chosen_index !== undefined ? q.options[q.chosen_index] : "Not Answered"}</p>
          <p><strong>Correct Answer:</strong> {q.options[q.correct_index]}</p>
          <p><strong>Reasoning:</strong> {q.reasoning}</p>
          <hr />
        </div>
      ))}
    </div>
  );
}
