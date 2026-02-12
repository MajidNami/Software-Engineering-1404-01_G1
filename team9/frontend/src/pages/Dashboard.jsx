import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import settingsIcon from "../assets/team9/images/settings.png";
import config from "../config";

export default function Dashboard() {
  const navigate = useNavigate();

  // State for user data
  const [user, setUser] = useState({
    name: "کاربر",
    totalLessons: 0,
    totalWords: 0,
    completedLessons: 0,
    averageProgress: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch dashboard data from API
  useEffect(() => {
    fetch(config.DASHBOARD_ENDPOINT, {
      credentials: 'include', // Include cookies for authentication
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("خطا در دریافت اطلاعات داشبورد");
        }
        return res.json();
      })
      .then((data) => {
        setUser({
          name: data.user_name || "کاربر",
          totalLessons: data.total_lessons,
          totalWords: data.total_words,
          completedLessons: data.completed_lessons,
          averageProgress: data.average_progress,
        });
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching dashboard data:", err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="container" dir="rtl" lang="fa">
        <div style={{ textAlign: "center", padding: "40px" }}>
          در حال بارگذاری...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" dir="rtl" lang="fa">
        <div style={{ textAlign: "center", padding: "40px", color: "red" }}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container" dir="rtl" lang="fa">
      <header className="header">
        <div className="header-right">
          <button 
            onClick={() => navigate("/microservices")} 
            className="home-btn"
          >
            میکروسرویس‌ها
          </button>
        </div>

        <div className="header-left">
          <div className="login-container">
            <div className="user-avatar" aria-hidden="true">
              <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="15" cy="10" r="5" fill="#647eb4" />
                <path d="M5 25C5 20 9 17 15 17C21 17 25 20 25 25" stroke="#647eb4" strokeWidth="2" fill="none" />
              </svg>
            </div>

            <a href="#" className="login-text">
              خروج
            </a>
          </div>

          <div className="flag-settings">
            <div className="iran-flag">
              <div className="flag-green"></div>
              <div className="flag-white"></div>
              <div className="flag-red"></div>
            </div>

            <img src={settingsIcon} alt="settings" className="settings-icon" />
          </div>
        </div>
      </header>

      <main style={{ padding: "40px 20px" }}>
        <div style={{ 
          maxWidth: "800px", 
          margin: "0 auto", 
          backgroundColor: "white", 
          borderRadius: "20px", 
          padding: "40px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)"
        }}>
          <h1 style={{ 
            fontSize: "2.5rem", 
            color: "var(--navy)", 
            textAlign: "center",
            marginBottom: "10px",
            fontFamily: "Vazirmatn, sans-serif"
          }}>
            داشبورد شخصی
          </h1>
          
          <h2 style={{ 
            fontSize: "1.5rem", 
            color: "#265BCF", 
            textAlign: "center",
            marginBottom: "40px",
            fontFamily: "Vazirmatn, sans-serif"
          }}>
            {user.name}
          </h2>

          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", 
            gap: "20px",
            marginBottom: "40px"
          }}>
            <div style={{
              backgroundColor: "#f4f9ff",
              padding: "25px",
              borderRadius: "15px",
              textAlign: "center"
            }}>
              <div style={{ fontSize: "2.5rem", fontWeight: "bold", color: "#265BCF" }}>
                {user.totalLessons}
              </div>
              <div style={{ fontSize: "1.1rem", color: "#0C1767", marginTop: "8px" }}>
                کل دروس
              </div>
            </div>

            <div style={{
              backgroundColor: "#f4f9ff",
              padding: "25px",
              borderRadius: "15px",
              textAlign: "center"
            }}>
              <div style={{ fontSize: "2.5rem", fontWeight: "bold", color: "#265BCF" }}>
                {user.totalWords}
              </div>
              <div style={{ fontSize: "1.1rem", color: "#0C1767", marginTop: "8px" }}>
                کل واژه‌ها
              </div>
            </div>

            <div style={{
              backgroundColor: "#f4f9ff",
              padding: "25px",
              borderRadius: "15px",
              textAlign: "center"
            }}>
              <div style={{ fontSize: "2.5rem", fontWeight: "bold", color: "#265BCF" }}>
                {user.completedLessons}
              </div>
              <div style={{ fontSize: "1.1rem", color: "#0C1767", marginTop: "8px" }}>
                دروس تکمیل شده
              </div>
            </div>

            <div style={{
              backgroundColor: "#f4f9ff",
              padding: "25px",
              borderRadius: "15px",
              textAlign: "center"
            }}>
              <div style={{ fontSize: "2.5rem", fontWeight: "bold", color: "#265BCF" }}>
                {user.averageProgress.toFixed(1)}%
              </div>
              <div style={{ fontSize: "1.1rem", color: "#0C1767", marginTop: "8px" }}>
                میانگین پیشرفت
              </div>
            </div>
          </div>

          <div style={{ textAlign: "center", marginTop: "40px" }}>
            <button
              onClick={() => navigate("/microservices")}
              style={{
                backgroundColor: "#ffd36b",
                border: "0",
                borderRadius: "20px",
                padding: "16px 40px",
                fontSize: "1.2rem",
                fontWeight: "bold",
                color: "#0C1767",
                cursor: "pointer",
                fontFamily: "Vazirmatn, sans-serif"
              }}
            >
              بازگشت به صفحه اصلی
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
