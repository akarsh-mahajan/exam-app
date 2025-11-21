import React from "react";
import { useLocation } from "react-router-dom";

export default function Result() {
  const { state } = useLocation();
  const { result } = state || {};

  if (!result) return <p>No results to display</p>;

  const { correct, wrong, unattempted, details, total_questions } = result;

  return (
    <div className="container">
      <h2>Quiz Results</h2>
      <p><strong>Total Questions:</strong> {total_questions}</p>
      <p><strong>Correct:</strong> {correct}</p>
      <p><strong>Wrong:</strong> {wrong}</p>
      <p><strong>Unattempted:</strong> {unattempted}</p>

      <h3>Details</h3>
      {details.map((q) => (
        <div key={q.question_id} className="result-question">
          <p><strong>Q:</strong> {q.question}</p>
          <p>
            <strong>Your Answer:</strong>{" "}
            {q.chosen_index !== null && q.chosen_index !== undefined
              ? q.options[q.chosen_index]
              : "Not answered"}
          </p>
          <p><strong>Correct Answer:</strong> {q.options[q.correct_index]}</p>
          <p><strong>Reasoning:</strong> {q.reasoning}</p>
          <hr />
        </div>
      ))}
    </div>
  );
}
