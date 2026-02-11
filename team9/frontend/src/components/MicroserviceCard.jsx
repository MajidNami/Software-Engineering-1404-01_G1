import { useNavigate } from "react-router-dom";

export default function MicroserviceCard({
  id,
  titleNode,
  title,
  words,
  progress,
  onDelete,
  disableNav = false,
}) {
  const navigate = useNavigate();

  const handleCardClick = () => {
    if (disableNav) return;
    if (id) navigate(`/microservices/${id}`);
  };

  return (
    <div
      className="t9-card"
      onClick={handleCardClick}
      style={{ cursor: disableNav ? "default" : "pointer" }}
    >
      <h3 className="t9-card__title">{titleNode ?? title}</h3>

      <div className="t9-card__meta">
        <div className="t9-card__metaRow">{words} کلمه</div>
        <div className="t9-card__metaRow">{progress}% پیشرفت</div>
      </div>

      <button
        className="t9-card__deleteBtn"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        حذف درس
      </button>
    </div>
  );
}
