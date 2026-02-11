// src/services/mockMicroservices.js
export const microservices = [
  {
    id: 1,
    title: "زبان عمومی",
    words: 6,
    progress: 20,
    wordList: [
      { fa: "کتاب", en: "Book" },
      { fa: "مداد", en: "Pencil" },
      { fa: "مدرسه", en: "School" },
      { fa: "دوست", en: "Friend" },
      { fa: "خانه", en: "Home" },
      { fa: "کار", en: "Work" },
    ],
  },
  {
    id: 2,
    title: "زبان تخصصی",
    words: 5,
    progress: 40,
    wordList: [
      { fa: "پایگاه داده", en: "Database" },
      { fa: "سرور", en: "Server" },
      { fa: "درخواست", en: "Request" },
      { fa: "پاسخ", en: "Response" },
      { fa: "احراز هویت", en: "Authentication" },
    ],
  },
  {
    id: 3,
    title: "روزمره",
    words: 4,
    progress: 10,
    wordList: [
      { fa: "صبح بخیر", en: "Good morning" },
      { fa: "ممنون", en: "Thanks" },
      { fa: "لطفاً", en: "Please" },
      { fa: "خداحافظ", en: "Goodbye" },
    ],
  },
];
