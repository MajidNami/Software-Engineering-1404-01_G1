import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { type ReactNode } from "react"; // <--- تغییر ۱: ایمپورت ReactNode
import { AuthProvider, useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import GrammarCheck from "./pages/GrammarCheck";
import DashboardHome from "./pages/Dashboard";
import Exercises from "./pages/Exercises";
import Stats from "./pages/Stats";

// --- Route Guard ---
// تغییر ۲: استفاده از ReactNode به جای JSX.Element
const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Route */}
          <Route path="/login" element={<Login />} />

          {/* Protected Routes */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<DashboardHome />} />
            <Route path="/check" element={<GrammarCheck />} />
            <Route path="/stats" element={<Stats />} />
            <Route path="/exercises" element={<Exercises />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
