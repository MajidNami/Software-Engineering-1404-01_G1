import { useParams, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import config from "../config";

export default function MicroserviceDetail() {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${config.API_BASE_URL}/team9/api/lessons/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        setItem(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching lesson:", err);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="container" dir="rtl" lang="fa">
        <h2 style={{ color: "var(--navy)" }}>در حال بارگذاری...</h2>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="container" dir="rtl" lang="fa">
        <h2 style={{ color: "var(--navy)" }}>موردی پیدا نشد</h2>
        <Link to="/microservices" className="home-btn" style={{ display: "inline-block", marginTop: 16 }}>
          برگشت به لیست
        </Link>
      </div>
    );
  }

  const wordCount = Array.isArray(item.words) ? item.words.length : 0;
  const progress = item.progress_percent || 0;

  return (
    <div className="container" dir="rtl" lang="fa">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 24 }}>
        <h2 style={{ fontSize: 24, color: "var(--navy)" }}>{item.title}</h2>

        <Link to="/microservices" className="home-btn">
          برگشت
        </Link>
      </div>

      <div style={{ marginTop: 16, background: "var(--white)", padding: 16, borderRadius: 16 }}>
        <p style={{ marginBottom: 8 }}>{wordCount} کلمه</p>
        <p>{progress.toFixed(1)}% پیشرفت</p>
      </div>
    </div>
  );
}
