import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { fetchExamSessionDetail } from "../api";

export default function ExamSessionDetails() {
  const { uuid } = useParams();
  const [session, setSession] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getSessionDetails = async () => {
      try {
        const response = await fetchExamSessionDetail(uuid);
        setSession(response.data);
      } catch (error) {
        setError("Error fetching exam session details.");
        console.error("Error fetching exam session details:", error);
      }
    };

    getSessionDetails();
  }, [uuid]);

  if (error) {
    return <div className="container">{error}</div>;
  }

  if (!session) {
    return <div className="container">Loading...</div>;
  }

  const getOptionClassName = (optionIndex, chosenIndex, correctIndex) => {
    if (chosenIndex === optionIndex) {
      return chosenIndex === correctIndex ? "option correct" : "option wrong";
    }
    return optionIndex === correctIndex ? "option correct" : "option";
  };

  return (
    <div className="container">
      <h1>Exam Session Details</h1>
      <h2>Topic: {session.topic.title}</h2>
      <p>Date: {new Date(session.finished_at).toLocaleString()}</p>
      <p>
        Score: {session.correct} / {session.total}
      </p>

      <div className="question-list">
        {session.details.map((detail, index) => (
          <div key={detail.question_id} className="question-card">
            <h4>
              Question {index + 1}: {detail.question}
            </h4>
            <ul className="option-list">
              {detail.options.map((option, optionIndex) => (
                <li
                  key={optionIndex}
                  className={getOptionClassName(
                    optionIndex,
                    detail.chosen_index,
                    detail.correct_index
                  )}
                >
                  {option}
                </li>
              ))}
            </ul>
            <div className="reasoning">
              <strong>Reasoning:</strong> {detail.reasoning}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
