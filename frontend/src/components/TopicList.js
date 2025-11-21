import React, { useEffect, useState } from "react";
import { fetchTopics } from "../api";
import { Link } from "react-router-dom";

export default function TopicList() {
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    fetchTopics().then((res) => setTopics(res.data));
  }, []);

  return (
    <div>
      <h2>Available Topics</h2>

      {topics.length === 0 ? <p>No topics found.</p> : null}

      <ul>
        {topics.map((t) => (
          <li key={t.id}>
            <Link to={`/topic/${t.id}`}>{t.title}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
