import React, { useState } from "react";
import { uploadPDF } from "../api";

export default function UploadPDF() {
  const [pdf, setPdf] = useState(null);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!pdf || !topic) {
      alert("Select a PDF and enter a topic name!");
      return;
    }

    setLoading(true);

    try {
      await uploadPDF(pdf, topic);
      alert("Questions generated successfully!");
      window.location.reload();
    } catch (err) {
      alert("Upload failed");
    }

    setLoading(false);
  };

  return (
    <div>
      <h2>Upload Study PDF</h2>

      <input
        type="text"
        placeholder="Enter topic name"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
      />

      <input type="file" onChange={(e) => setPdf(e.target.files[0])} />

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload PDF"}
      </button>
    </div>
  );
}
