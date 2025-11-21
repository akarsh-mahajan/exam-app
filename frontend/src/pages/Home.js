import React from "react";
import UploadPDF from "../components/UploadPDF";
import TopicList from "../components/TopicList";
import { clearDatabase } from "../api";

export default function Home() {
  const handleClearDatabase = async () => {
    if (window.confirm("Are you sure you want to clear the entire database? This action cannot be undone.")) {
      try {
        await clearDatabase();
        alert("Database cleared successfully.");
        window.location.reload();
      } catch (error) {
        alert("Error clearing the database.");
        console.error("Error clearing database:", error);
      }
    }
  };

  return (
    <div className="container">
      <h1>📘 Objective Exam Preparation App</h1>

      <UploadPDF />
      <hr />
      <TopicList />

      <div className="danger-zone">
        <button className="btn-danger" onClick={handleClearDatabase}>
          Clear Database
        </button>
      </div>
    </div>
  );
}
