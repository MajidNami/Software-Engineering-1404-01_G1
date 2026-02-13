import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import config from "../config";

function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default function AddWord() {
  const navigate = useNavigate();

  const [word, setWord] = useState("");
  const [meaning, setMeaning] = useState("");
  const [selected, setSelected] = useState(null);
  const [lessons, setLessons] = useState([]);

 
  useEffect(() => {
    fetch(config.LESSONS_ENDPOINT)
      .then((res) => res.json())
      .then((data) => setLessons(data))
      .catch((err) => console.error("Error fetching lessons:", err));
  }, []);

  const handleAddWord = () => {
    if (!word || !meaning || !selected) {
      alert("لطفاً تمامی فیلدها را پر کرده و یک درس را انتخاب کنید.");
      return;
    }

    const csrfToken = getCsrfToken();
    fetch(config.WORDS_ENDPOINT, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      credentials: "include",
      body: JSON.stringify({
        term: word,         
        definition: meaning,  
        lesson: selected,
        user_id: 1 
      }),
    })
      .then((res) => {
        if (res.ok) {
          alert("واژه با موفقیت افزوده شد.");
          navigate("/microservices");
        } else {
          
          res.json().then(data => console.error("Validation Errors:", data));
          alert("خطایی در ثبت واژه رخ داد. کنسول را چک کنید.");
        }
      })
      .catch((err) => console.error("Error posting word:", err));
  };

  return (
    <div className="t9-page" dir="rtl" lang="fa">
      <header className="t9-topbar">
        <button className="t9-pillBtn" onClick={() => window.location.href = "http://localhost:8000"}>خانه</button>
        <h1 className="t9-title">یادگیری مستمر با Tick 8</h1>
        <Link to="/dashboard" className="t9-pillBtn" style={{textDecoration: 'none'}}>حساب کاربری</Link>
      </header>

      <section className="t9-panel t9-addword">
        <div className="t9-form">
          <label className="t9-label">
            <span>واژه را وارد کنید:</span>
            <input
              className="t9-input"
              value={word}
              onChange={(e) => setWord(e.target.value)}
            />
          </label>

          <label className="t9-label">
            <span>معنی واژه:</span>
            <input
              className="t9-input"
              value={meaning}
              onChange={(e) => setMeaning(e.target.value)}
            />
          </label>

          <label className="t9-label">
            <span>انتخاب درس مورد نظر:</span>
            <div className="t9-line"></div>
          </label>

          <div className="t9-lessonBox">
            {lessons.map((l) => (
              <button
                key={l.id}
                type="button"
                className={`t9-lessonBtn ${selected === l.id ? "is-active" : ""}`}
                onClick={() => setSelected(l.id)}
              >
                {l.title}
              </button>
            ))}
          </div>

          <div className="t9-addwordActions">
            <button className="t9-actionBtn" type="button" onClick={handleAddWord}>
              افزودن واژه
            </button>
            
            <button className="t9-actionBtn" type="button" onClick={() => navigate(-1)}>
              بازگشت
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}