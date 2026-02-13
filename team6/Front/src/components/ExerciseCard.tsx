import { type Exercise } from "../types/api";
import { Check, X, RotateCcw } from "lucide-react";

interface Props {
  exercise: Exercise;
  userAnswer: string;
  onAnswer: (answer: string) => void;
  isSubmitted: boolean;
  isCorrect?: boolean;
  correctAnswer?: string;
}

export default function ExerciseCard({
  exercise,
  userAnswer,
  onAnswer,
  isSubmitted,
  isCorrect,
  correctAnswer,
}: Props) {
  // --- Render Logic based on Type ---

  const renderContent = () => {
    switch (exercise.exerciseType) {
      case "MULTIPLE_CHOICE":
      case "FILL_BLANK": // Treating Fill Blank with options similarly for better UX
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
            {exercise.options.map((opt) => (
              <button
                key={opt}
                disabled={isSubmitted}
                onClick={() => onAnswer(opt)}
                className={`px-4 py-3 rounded-xl border-2 text-left transition-all ${
                  userAnswer === opt
                    ? "border-primary bg-primary-light text-primary font-medium"
                    : "border-gray-100 hover:border-gray-300 text-dark-800 bg-white"
                } ${isSubmitted && userAnswer !== opt ? "opacity-50" : ""}`}
              >
                {opt}
              </button>
            ))}
          </div>
        );

      case "FULL_SENTENCE":
        // Logic: User clicks words to build a sentence
        const currentWords = userAnswer ? userAnswer.split(" ") : [];
        const availableWords = exercise.options.filter(
          (word) =>
            // Simple logic to hide used words (handling duplicates might need index tracking)
            !currentWords.includes(word) ||
            exercise.options.filter((w) => w === word).length >
              currentWords.filter((w) => w === word).length,
        );

        return (
          <div className="mt-4 space-y-4">
            {/* Building Area */}
            <div className="min-h-[60px] p-4 bg-gray-50 rounded-xl border-b-2 border-gray-200 flex flex-wrap gap-2">
              {currentWords.map((word, idx) => (
                <button
                  key={idx}
                  disabled={isSubmitted}
                  onClick={() => {
                    const newWords = [...currentWords];
                    newWords.splice(idx, 1);
                    onAnswer(newWords.join(" "));
                  }}
                  className="px-3 py-1.5 bg-white border border-gray-200 shadow-sm rounded-lg text-dark-900 font-medium hover:bg-red-50 hover:text-red-500 transition-colors"
                >
                  {word}
                </button>
              ))}
              {currentWords.length === 0 && (
                <span className="text-gray-400 text-sm italic self-center">
                  Tap words below to build the sentence
                </span>
              )}
            </div>

            {/* Word Bank */}
            <div className="flex flex-wrap gap-2">
              {availableWords.map((word, idx) => (
                <button
                  key={`${word}-${idx}`}
                  disabled={isSubmitted}
                  onClick={() =>
                    onAnswer(userAnswer ? `${userAnswer} ${word}` : word)
                  }
                  className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-dark-800 hover:bg-gray-50 hover:border-gray-300 transition-all"
                >
                  {word}
                </button>
              ))}
            </div>

            <button
              onClick={() => onAnswer("")}
              disabled={!userAnswer || isSubmitted}
              className="text-xs text-gray-500 flex items-center gap-1 hover:text-dark-900"
            >
              <RotateCcw size={12} /> Reset
            </button>
          </div>
        );

      default:
        return <p className="text-red-500">Unknown exercise type</p>;
    }
  };

  return (
    <div
      className={`p-6 rounded-2xl border-2 transition-all ${
        isSubmitted
          ? isCorrect
            ? "bg-green-50 border-green-200"
            : "bg-red-50 border-red-200"
          : "bg-white border-transparent shadow-soft"
      }`}
    >
      {/* Question Header */}
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-bold text-dark-900">{exercise.question}</h3>
        {isSubmitted &&
          (isCorrect ? (
            <div className="p-1 bg-green-100 text-green-600 rounded-full">
              <Check size={20} />
            </div>
          ) : (
            <div className="p-1 bg-red-100 text-red-600 rounded-full">
              <X size={20} />
            </div>
          ))}
      </div>

      <div className="flex gap-2 mb-4">
        <span className="text-xs font-bold px-2 py-0.5 rounded bg-gray-100 text-gray-500 uppercase tracking-wider">
          {exercise.grammarTopic.replace("_", " ")}
        </span>
        <span
          className={`text-xs font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
            exercise.grammarLevel === "EASY"
              ? "bg-green-100 text-green-700"
              : exercise.grammarLevel === "MEDIUM"
                ? "bg-yellow-100 text-yellow-700"
                : "bg-red-100 text-red-700"
          }`}
        >
          {exercise.grammarLevel}
        </span>
      </div>

      {renderContent()}

      {/* Feedback Footer */}
      {isSubmitted && !isCorrect && correctAnswer && (
        <div className="mt-4 pt-3 border-t border-red-200 text-sm text-red-800">
          <span className="font-bold">Correct Answer:</span> {correctAnswer}
        </div>
      )}
    </div>
  );
}
