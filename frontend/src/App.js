import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import TopicPage from "./pages/TopicPage";
import Quiz from "./components/Quiz";
import Result from "./components/Result";
import Header from "./components/Header";

import ExamSessionDetails from "./components/ExamSessionDetails";

import "./styles.css";

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/topic/:id" element={<TopicPage />} />
        <Route path="/topic/:id/quiz" element={<Quiz />} />
        <Route path="/topic/:id/result" element={<Result />} />
        <Route path="/session/:uuid" element={<ExamSessionDetails />} />
      </Routes>
    </BrowserRouter>
  );
}
