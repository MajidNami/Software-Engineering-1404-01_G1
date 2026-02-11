import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

export default function LessonDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [lesson, setLesson] = useState(null);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/team9/api/lessons/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        setLesson(data);
        const formattedWords = (data.words || []).map((w) => {
          
          const history = w.review_history || "00000000";
          const cellColors = Array.from(history).map((char) => {
            if (char === "1") return "green";  
            if (char === "2") return "orange"; 
            return "empty";                    
          });

          return {
            id: w.id,
            en: w.term,
            fa: w.definition,
            status: w.is_learned ? "learned" : "none",
            last_review_date: w.last_review_date,
            review_history: history, 
            cells: cellColors,
          };
        });
        setRows(formattedWords);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching lesson detail:", err);
        setLoading(false);
      });
  }, [id]);

  const learnedCount = rows.filter((r) => r.status === "learned").length;
  const total = rows.length;
  const progressPct = total === 0 ? 0 : Math.round((learnedCount / total) * 100);

  const mark = (rowId, type) => {
    const today = new Date().toISOString().split('T')[0];
    const currentRow = rows.find(r => r.id === rowId);
    if (!currentRow) return;

    if (currentRow.last_review_date === today) {
      alert("تیک بعدی فردا! شما امروز این کلمه را مطالعه کرده‌اید.");
      return;
    }

    
    const historyArray = Array.from(currentRow.review_history);
    const targetIdx = historyArray.indexOf('0');

    if (targetIdx === -1) return;

    
    const newChar = type === "know" ? "1" : "2";
    historyArray[targetIdx] = newChar;
    const newHistoryStr = historyArray.join('');

    
    const greenCount = historyArray.filter(c => c === "1").length;
    const isNowLearned = greenCount >= 6;

    
    fetch(`http://127.0.0.1:8000/team9/api/words/${rowId}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        current_day: targetIdx + 1,
        review_history: newHistoryStr, 
        is_learned: isNowLearned,
        last_review_date: today
      }),
    })
    .then(res => res.json())
    .then(() => {
      setRows((prev) =>
        prev.map((r) => {
          if (r.id !== rowId) return r;
          return {
            ...r,
            review_history: newHistoryStr,
            status: isNowLearned ? "learned" : type,
            cells: historyArray.map(c => c === "1" ? "green" : c === "2" ? "orange" : "empty"),
            last_review_date: today
          };
        })
      );
    })
    .catch(err => console.error("Update Error:", err));
  };

  const removeWord = (rowId) => {
    if(!window.confirm("حذف شود؟")) return;
    fetch(`http://127.0.0.1:8000/team9/api/words/${rowId}/`, { method: "DELETE" })
      .then(() => setRows(prev => prev.filter(r => r.id !== rowId)));
  };

  if (loading) return <div className="t9-page" dir="rtl">در حال بارگذاری...</div>;

  return (
    <div className="t9-page" dir="rtl" lang="fa">
      <header className="t9-topbar t9-topbar--detail">
        <div className="t9-topbarLeft">
          <button className="t9-pillBtn" onClick={() => navigate("/microservices")}>بازگشت</button>
          <button className="t9-pillBtn" onClick={() => navigate(`/microservices/${id}/review`)}>مرور لغات</button>
        </div>
        <h1 className="t9-title">{lesson?.title}</h1>
      </header>

      <section className="t9-panel">
        <div className="t9-lessonMeta">
          <div>تعداد کلمات: {total}</div>
          <div>پیشرفت: %{progressPct}</div>
        </div>

        <div className="t9-wordsBox">
          {rows.map((r) => (
            <div className="t9-wordRow" key={r.id}>
              <div className="t9-wordEn">{r.en}</div>
              <div className="t9-wordActions">
                {r.status === "learned" ? (
                  <span className="t9-learnedTag">یاد گرفته شده</span>
                ) : (
                  <>
                    <button className="t9-chip t9-chip--green" onClick={() => mark(r.id, "know")}>میدانم</button>
                    <button className="t9-chip t9-chip--orange" onClick={() => mark(r.id, "dontknow")}>نمیدانم</button>
                  </>
                )}
              </div>
              <div className="t9-cells">
                {r.cells.map((c, i) => (
                  <span
                    key={i}
                    className={`t9-cell ${c === "green" ? "t9-cell--green" : ""} ${c === "orange" ? "t9-cell--orange" : ""}`}
                  />
                ))}
              </div>
              <button className="t9-trashBtn" onClick={() => removeWord(r.id)}>🗑️</button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}