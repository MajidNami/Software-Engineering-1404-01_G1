import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import api from "../api/axios";
import {
  type Exercise,
  type GrammarTopic,
  type GrammarLevel,
} from "../types/api";
import ExerciseCard from "../components/ExerciseCard";
import { Loader2, CheckCircle, Send } from "lucide-react";

export default function Exercises() {
  // State for filters
  const [selectedTopic, setSelectedTopic] =
    useState<GrammarTopic>("PRESENT_SIMPLE");
  const [selectedLevel, setSelectedLevel] = useState<GrammarLevel>("MEDIUM");

  // State for user answers: { [exerciseId]: "answer string" }
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [results, setResults] = useState<
    Record<number, { isCorrect: boolean; correctAnswer?: string }>
  >({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  // 1. Fetch Exercises — backend requires both grammarTopic and grammarLevel
  const { data: exercises, isLoading } = useQuery({
    queryKey: ["exercises", selectedTopic, selectedLevel],
    queryFn: async () => {
      const res = await api.get<{ exercises: Exercise[] }>("/exercises", {
        params: { grammarTopic: selectedTopic, grammarLevel: selectedLevel },
      });
      return res.data.exercises;
    },
  });

  // 2. Submit Mutation
  const submitMutation = useMutation({
    mutationFn: async () => {
      //[cite_start]// Formatting payload as per API requirement [cite: 99]
      const payload = {
        answers: Object.entries(answers).map(([id, ans]) => ({
          exerciseId: Number(id),
          answer: ans,
        })),
      };

      const res = await api.post("/exercises/answer", payload);
      return res.data;
      // Expected response: { results: [{ exerciseId: 55, isCorrect: true, ... }] }
    },
    onSuccess: (data: any) => {
      const resultMap: any = {};
      data.results.forEach((r: any) => {
        resultMap[r.exerciseId] = {
          isCorrect: r.correct ?? r.isCorrect,
          correctAnswer: r.correctAnswer,
        };
      });
      setResults(resultMap);
      setIsSubmitted(true);
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
  });

  const handleAnswerChange = (id: number, val: string) => {
    if (isSubmitted) return;
    setAnswers((prev) => ({ ...prev, [id]: val }));
  };

  if (isLoading)
    return (
      <div className="flex justify-center p-20">
        <Loader2 className="animate-spin text-primary" size={40} />
      </div>
    );

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-20">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-dark-900">Practice Arena</h1>
          <p className="text-gray-500 mt-1">
            Sharpen your skills with targeted exercises.
          </p>
        </div>

        {/* Topic & Level Selectors */}
        <div className="flex flex-wrap gap-3 items-center">
          <select
            value={selectedTopic}
            onChange={(e) => {
              setSelectedTopic(e.target.value as GrammarTopic);
              setAnswers({});
              setResults({});
              setIsSubmitted(false);
            }}
            className="px-4 py-2 rounded-xl bg-white border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20 text-sm shadow-sm"
          >
            <option value="PRESENT_SIMPLE">Present Simple</option>
            <option value="PRESENT_CONTINUOUS">Present Continuous</option>
            <option value="PAST_SIMPLE">Past Simple</option>
            <option value="PAST_CONTINUOUS">Past Continuous</option>
            <option value="PRESENT_PERFECT">Present Perfect</option>
            <option value="TENSE_CHOICE">Tense Choice</option>
            <option value="CONDITIONAL_FIRST">Conditional First</option>
            <option value="CONDITIONAL_SECOND">Conditional Second</option>
            <option value="PASSIVE_VOICE">Passive Voice</option>
            <option value="ARTICLES">Articles</option>
            <option value="COMPARISON">Comparison</option>
            <option value="GERUND_INFINITIVE">Gerund / Infinitive</option>
            <option value="RELATIVE_CLAUSES">Relative Clauses</option>
            <option value="REPORTED_SPEECH">Reported Speech</option>
          </select>

          <div className="flex bg-gray-100 p-1 rounded-lg">
            {(["EASY", "MEDIUM", "HARD"] as GrammarLevel[]).map((level) => (
              <button
                key={level}
                onClick={() => {
                  setSelectedLevel(level);
                  setAnswers({});
                  setResults({});
                  setIsSubmitted(false);
                }}
                className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                  selectedLevel === level
                    ? "bg-white text-primary shadow-sm"
                    : "text-gray-500 hover:text-dark-900"
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
        {isSubmitted && (
          <div className="bg-green-100 text-green-700 px-4 py-2 rounded-xl font-bold flex items-center gap-2">
            <CheckCircle size={20} />
            Score: {
              Object.values(results).filter((r) => r.isCorrect).length
            } / {exercises?.length}
          </div>
        )}
      </div>

      <div className="space-y-6">
        {exercises?.map((ex) => (
          <ExerciseCard
            key={ex.id}
            exercise={ex}
            userAnswer={answers[ex.id] || ""}
            onAnswer={(val) => handleAnswerChange(ex.id, val)}
            isSubmitted={isSubmitted}
            isCorrect={results[ex.id]?.isCorrect}
            correctAnswer={results[ex.id]?.correctAnswer}
          />
        ))}
      </div>

      {/* Floating Submit Button */}
      {!isSubmitted && exercises && exercises.length > 0 && (
        <div className="sticky bottom-6 flex justify-center">
          <button
            onClick={() => submitMutation.mutate()}
            disabled={
              submitMutation.isPending ||
              Object.keys(answers).length < exercises.length
            }
            className="bg-dark-900 hover:bg-black text-white px-8 py-4 rounded-full shadow-2xl flex items-center gap-3 font-bold transition-transform hover:-translate-y-1 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {submitMutation.isPending ? (
              <Loader2 className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
            {Object.keys(answers).length < exercises.length
              ? `Answer all questions (${Object.keys(answers).length}/${exercises.length})`
              : "Submit Answers"}
          </button>
        </div>
      )}

      {isSubmitted && (
        <div className="flex justify-center pt-8">
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-secondary text-white rounded-xl font-medium shadow-lg hover:bg-secondary-dark transition-colors"
          >
            Start New Session
          </button>
        </div>
      )}
    </div>
  );
}
