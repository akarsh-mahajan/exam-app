import React, { useEffect, useState } from "react";
import { fetchQuiz, submitQuiz, endExam } from "../api";
import { useParams, useNavigate } from "react-router-dom";

export default function Quiz() {
  const { id } = useParams(); // topic id
  const navigate = useNavigate();

  const [questions, setQuestions] = useState([]);
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [quizUuid, setQuizUuid] = useState(null);

  useEffect(() => {
    fetchQuiz(id).then((res) => {
      setQuestions(res.data.questions || []);
      setQuizUuid(res.data.uuid);
    });
  }, [id]);

  const handleSelect = (qId, optionIndex) => {
    setAnswers({ ...answers, [qId]: optionIndex });
  };

  const handleSubmit = async () => {
    if (!quizUuid) return;

    try {
      // 1️⃣ Submit all answers
      await submitQuiz(quizUuid, answers);

      // 2️⃣ End exam & get results
      const res = await endExam(quizUuid);

      navigate(`/topic/${id}/result`, { state: { result: res.data } });
    } catch (err) {
      console.error("Error submitting quiz:", err);
    }
  };

  if (!questions.length) return <p>Loading...</p>;

  const current = questions[index];

  return (
    <div className="container">
      <h2>
        Question {index + 1} / {questions.length}
      </h2>
      <p>{current.question}</p>

      {current.options.map((opt, i) => (
        <div key={i}>
          <input
            type="radio"
            name={current.id}
            checked={answers[current.id] === i}
            onChange={() => handleSelect(current.id, i)}
          />
          {opt}
        </div>
      ))}

      <div className="buttons">
        <button disabled={index === 0} onClick={() => setIndex(index - 1)}>
          Previous
        </button>

        <button
          disabled={index === questions.length - 1}
          onClick={() => setIndex(index + 1)}
        >
          Next
        </button>

        <button onClick={handleSubmit}>Submit Quiz</button>
      </div>
    </div>
  );
}
