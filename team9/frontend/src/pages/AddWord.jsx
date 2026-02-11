import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function AddWord() {
  const navigate = useNavigate();

  const [word, setWord] = useState("");
  const [meaning, setMeaning] = useState("");
  const [selected, setSelected] = useState(null);
  const [lessons, setLessons] = useState([]);

 
  useEffect(() => {
    fetch("http://127.0.0.1:8000/team9/api/lessons/")
      .then((res) => res.json())
      .then((data) => setLessons(data))
      .catch((err) => console.error("Error fetching lessons:", err));
  }, []);

  const handleAddWord = () => {
    if (!word || !meaning || !selected) {
      alert("لطفاً تمامی فیلدها را پر کرده و یک درس را انتخاب کنید.");
      return;
    }

   
    fetch("http://127.0.0.1:8000/team9/api/words/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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
        <button className="t9-pillBtn">حساب کاربری</button>
        <h1 className="t9-title">یادگیری مستمر با Tick 8</h1>
        <button className="t9-pillBtn" onClick={() => navigate("/microservices")}>
          خانه
        </button>
      </header>

      <section className="t9-panel t9-addword">
        <div className="t9-form">
          <label className="t9-label">
            <span>Enter Word:</span>
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

          <div className="t9-label">
            <span>انتخاب درس مورد نظر:</span>
          </div>

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
            <button className="t9-actionBtn" type="button" onClick={() => navigate(-1)}>
              بازگشت
            </button>

            <button
              className="t9-actionBtn"
              type="button"
              onClick={handleAddWord}
            >
              افزودن واژه
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}