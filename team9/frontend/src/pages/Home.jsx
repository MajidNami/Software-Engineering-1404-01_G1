import settingsIcon from "../assets/team9/images/settings.png";
import { Link } from "react-router-dom";

export default function Home() {
  const isLoggedIn = false;

  return (
    <div className="container" dir="rtl" lang="fa">
      <header className="header">
        <div className="header-right">
          <Link to="/microservices" className="home-btn">
            میکروسرویس‌ها
          </Link>
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
              {isLoggedIn ? "خروج" : "ورود"}
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

      <main className="welcome-section">
        <h1 style={{ fontSize: "3rem", color: "var(--navy)" }}>
          به میکروسرویس گروه 9 خوش آمدید
        </h1>
      </main>
    </div>
  );
}
