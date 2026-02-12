import { Routes, Route, Navigate } from "react-router-dom";
import Microservices from "./pages/Microservices";
import AddWord from "./pages/AddWord";
import LessonDetail from "./pages/LessonDetail";
import ReviewLesson from "./pages/ReviewLesson";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";

export default function App() {
  return (
    <Routes>

      <Route path="/" element={<Microservices />} />


      <Route path="/microservices" element={<Microservices />} />

      
      <Route path="/microservices/:id" element={<LessonDetail />} />

      
      <Route path="/microservices/:id/review" element={<ReviewLesson />} />

      
      <Route path="/add-word" element={<AddWord />} />

      
      <Route path="/dashboard" element={<Dashboard />} />

      
      <Route path="*" element={<Navigate to="/microservices" replace />} />
    </Routes>
  );
}
