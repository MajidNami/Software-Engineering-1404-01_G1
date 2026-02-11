import { useMemo, useState, useEffect } from "react";
import MicroserviceCard from "../components/MicroserviceCard";
import { Link } from "react-router-dom";

export default function Microservices() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch initial data from Django
  useEffect(() => {
    fetch("http://127.0.0.1:8000/team9/api/lessons/")
      .then((res) => res.json())
      .then((data) => {
        setItems(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching lessons:", err);
        setLoading(false);
      });
  }, []);

  const filtered = useMemo(() => {
    const s = q.trim();
    if (!s) return items;
    return items.filter((x) => x.title && x.title.includes(s));
  }, [q, items]);

  const addLesson = () => {
    if (editingId) return;

    const newId = Date.now();
    const newItem = {
      id: newId,
      title: "",
      words: [], 
      progress: 0,
      isNew: true,
    };

    setItems((prev) => [newItem, ...prev]);
    setEditingId(newId);
  };

  const commitTitle = (id, value) => {
    const v = value.trim();
    const item = items.find((x) => x.id === id);

    if (!v) {
      setItems((prev) => prev.filter((x) => x.id !== id));
      setEditingId(null);
      return;
    }

    if (item?.isNew) {
      fetch("http://127.0.0.1:8000/team9/api/lessons/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          title: v,
          user_id: 1 
        }),
      })
        .then((res) => res.json())
        .then((savedItem) => {
          setItems((prev) =>
            prev.map((x) => (x.id === id ? savedItem : x))
          );
        })
        .catch(err => console.error("POST Error:", err));
    } else {
      fetch(`http://127.0.0.1:8000/team9/api/lessons/${id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: v }),
      })
        .then((res) => res.json())
        .then((updatedItem) => {
          setItems((prev) =>
            prev.map((x) => (x.id === id ? updatedItem : x))
          );
        })
        .catch(err => console.error("PATCH Error:", err));
    }

    setEditingId(null);
  };

  const deleteLesson = (id) => {
    fetch(`http://127.0.0.1:8000/team9/api/lessons/${id}/`, {
      method: "DELETE",
    }).then(() => {
      setItems((prev) => prev.filter((x) => x.id !== id));
    });
  };

  if (loading) return <div className="t9-page" dir="rtl">در حال بارگذاری...</div>;

  return (
    <div className="t9-page" dir="rtl" lang="fa">
      <header className="t9-topbar">
        <button className="t9-pillBtn">حساب کاربری</button>
        <h1 className="t9-title">یادگیری مستمر با Tick 8</h1>
        <button className="t9-pillBtn">خانه</button>
      </header>

      <section className="t9-panel">
        <div className="t9-searchRow">
          <span className="t9-searchIcon" aria-hidden="true">
            🔍
          </span>
          <input
            className="t9-search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="جستجو"
          />
        </div>

        <div className="t9-grid">
          {filtered.map((m) => {
            const isEditing = editingId === m.id;

            return (
              <MicroserviceCard
                key={m.id}
                id={m.id}
                disableNav={isEditing}
                title={m.title || "نام را وارد کنید"}
                titleNode={
                  isEditing ? (
                    <input
                      autoFocus
                      placeholder="نام را وارد کنید"
                      defaultValue={m.title || ""}
                      onClick={(e) => e.stopPropagation()}
                      onBlur={(e) => commitTitle(m.id, e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") e.currentTarget.blur();
                        if (e.key === "Escape") {
                          if (m.isNew) {
                            setItems((prev) => prev.filter((x) => x.id !== m.id));
                          }
                          setEditingId(null);
                        }
                      }}
                    />
                  ) : null
                }
                
                words={Array.isArray(m.words) ? m.words.length : (m.words || 0)}
                progress={m.progress}
                onDelete={() => deleteLesson(m.id)}
              />
            );
          })}
        </div>

        <div className="t9-actions">
          <Link className="t9-actionBtn" to="/add-word">
            افزودن واژه
          </Link>
          <button className="t9-actionBtn" onClick={addLesson}>
            افزودن درس
          </button>
        </div>
      </section>
    </div>
  );
}