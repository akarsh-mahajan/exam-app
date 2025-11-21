import React from "react";
import UploadPDF from "../components/UploadPDF";
import TopicList from "../components/TopicList";

export default function Home() {
  return (
    <div className="container">
      <h1>📘 Objective Exam Preparation App</h1>

      <UploadPDF />
      <hr />
      <TopicList />
    </div>
  );
}
