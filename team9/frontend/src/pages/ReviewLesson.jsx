import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import config from "../config";

export default function ReviewLesson() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [lesson, setLesson] = useState(null);
  const [words, setWords] = useState([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showMeaning, setShowMeaning] = useState(false);

  useEffect(() => {
    fetch(`${config.API_BASE_URL}/team9/api/lessons/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        setLesson(data);
        
        const toReview = (data.words || []).filter(w => !w.is_learned);
        setWords(toReview);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Review Fetch Error:", err);
        setLoading(false);
      });
  }, [id]);

  if (loading) return <div className="t9-page" dir="rtl">در حال بارگذاری...</div>;
  if (!lesson || words.length === 0) {
    return (
      <div className="t9-page" dir="rtl">
        <section className="t9-panel" style={{ textAlign: "center" }}>
          <h2>کلمه‌ای برای مرور نیست!</h2>
          <button className="t9-pillBtn" onClick={() => navigate(-1)}>بازگشت</button>
        </section>
      </div>
    );
  }

  const word = words[index];
  const today = new Date().toISOString().split('T')[0];

  const mark = (type) => {
    if (word.last_review_date === today) {
      alert("این کلمه را امروز مرور کرده‌اید.");
      return;
    }

    
    const historyArray = Array.from(word.review_history || "00000000");
    const targetIdx = historyArray.indexOf('0'); 

    if (targetIdx === -1) return;

    
    const newChar = type === "know" ? "1" : "2";
    historyArray[targetIdx] = newChar;
    const newHistoryStr = historyArray.join('');

    
    const greenCount = historyArray.filter(c => c === "1").length;
    const isNowLearned = greenCount >= 6;

    
    fetch(`${config.API_BASE_URL}/team9/api/words/${word.id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        current_day: targetIdx + 1,
        review_history: newHistoryStr, 
        last_review_date: today,
        is_learned: isNowLearned
      }),
    })
    .then((res) => res.json())
    .then((updatedWord) => {
      const newWords = [...words];
      newWords[index] = {
        ...updatedWord,
        en: updatedWord.term,
        fa: updatedWord.definition,
        review_history: newHistoryStr 
      };
      setWords(newWords);
      setShowMeaning(true);
    });
  };

  const handleNext = () => {
    setShowMeaning(false);
    setIndex((i) => i + 1);
  };

  const handlePrev = () => {
    setShowMeaning(false);
    setIndex((i) => i - 1);
  };

  return (
    <div className="t9-page" dir="rtl" lang="fa">
      <header className="t9-topbar">
        <button className="t9-pillBtn" onClick={() => navigate(`/microservices/${id}`)}>
          بازگشت
        </button>
        <h1 className="t9-title">مرور: {lesson.title}</h1>
        <button className="t9-pillBtn" onClick={() => window.location.href = "http://localhost:8000"}>
          خانه
        </button>
      </header>

      <section className="t9-panel t9-reviewBox">
        <div className="t9-reviewHeader">
          <span>کلمه {index + 1} از {words.length}</span>
        </div>

        <h2 className="t9-reviewWord">{word.term}</h2>

        <div className="t9-reviewActions">
          <button className="t9-chip t9-chip--green" onClick={() => mark("know")}>
            میدانم
          </button>
          <button className="t9-chip t9-chip--orange" onClick={() => mark("dont")}>
            نمیدانم
          </button>
        </div>

        
        <div className="t9-cells t9-cells--center">
          {Array.from(word.review_history || "00000000").map((char, i) => (
            <span
              key={i}
              className={`t9-cell 
                ${char === "1" ? "t9-cell--green" : ""} 
                ${char === "2" ? "t9-cell--orange" : ""} 
                ${char === "0" ? "" : ""}`}
            />
          ))}
        </div>

        <div className="t9-meaningArea">
          {showMeaning ? (
            <p className="t9-reviewMeaning">{word.definition}</p>
          ) : (
            <button className="t9-showBtn" onClick={() => setShowMeaning(true)}>
              مشاهده معنی
            </button>
          )}
        </div>

        <div className="t9-reviewNav">
          <button className="t9-pillBtn" disabled={index === 0} onClick={handlePrev}>
            قبلی
          </button>
          <button className="t9-pillBtn" disabled={index === words.length - 1} onClick={handleNext}>
            بعدی
          </button>
        </div>
      </section>
    </div>
  );
}