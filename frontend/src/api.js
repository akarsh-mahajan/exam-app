import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api/quiz";

// 1️⃣ Upload PDF and create topic
export const uploadPDF = (file, topic) => {
  const formData = new FormData();
  formData.append("pdf", file);
  formData.append("topic", topic);

  return axios.post(`${API_BASE}/upload/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// 2️⃣ Fetch all topics
export const fetchTopics = () => {
  return axios.get(`${API_BASE}/topics/`);
};

// 3️⃣ Start exam for a topic
export const fetchQuiz = (topicId) => {
  return axios.post(`${API_BASE}/start_exam/${topicId}/`);
};

// 4️⃣ Submit quiz answers
export const submitQuiz = (examUUID, answers) => {
  return axios.post(`${API_BASE}/submit_answer/${examUUID}/`, {
    answers,
  });
};

export const submitAnswer = (examUuid, data) => {
    return axios.post(`${API_BASE}/submit_answer/${examUuid}/`, data);
};

export const endExam = (examUuid) => {
    return axios.post(`${API_BASE}/end_exam/${examUuid}/`);
};

// fetch exam sessions list
export const fetchExamSessions = () => {
    return axios.get(`${API_BASE}/sessions/`);
  };
  
  // fetch detail for one session
  export const fetchExamSessionDetail = (uuid) => {
    return axios.get(`${API_BASE}/sessions/${uuid}/`);
  };
  