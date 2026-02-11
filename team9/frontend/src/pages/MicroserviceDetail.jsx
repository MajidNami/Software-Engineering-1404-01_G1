import { useParams, Link } from "react-router-dom";
import { microservices } from "../services/mockMicroservices";

export default function MicroserviceDetail() {
  const { id } = useParams();
  const item = microservices.find((m) => String(m.id) === String(id));

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

  return (
    <div className="container" dir="rtl" lang="fa">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 24 }}>
        <h2 style={{ fontSize: 24, color: "var(--navy)" }}>{item.title}</h2>

        <Link to="/microservices" className="home-btn">
          برگشت
        </Link>
      </div>

      <div style={{ marginTop: 16, background: "var(--white)", padding: 16, borderRadius: 16 }}>
        <p style={{ marginBottom: 8 }}>{item.countLabel}</p>
        <p>{item.progressLabel}</p>
      </div>
    </div>
  );
}
