import React from "react";
import { Link, useParams } from "react-router-dom";

export default function TopicPage() {
  const { id } = useParams();

  return (
    <div className="container">
      <h1>Topic #{id}</h1>

      <Link to={`/topic/${id}/quiz`}>
        <button>Start Quiz</button>
      </Link>
    </div>
  );
}
