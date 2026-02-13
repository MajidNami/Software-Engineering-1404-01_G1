import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import api from "../api/axios";
import {
  type EvaluateRequest,
  type EvaluateResponse,
  type EvaluationType,
} from "../types/api";
import {
  Loader2,
  CheckCircle2,
  XCircle,
  ArrowRight,
  BookOpen,
  Zap,
  FileText,
} from "lucide-react";

export default function GrammarCheck() {
  const [text, setText] = useState("");
  const [mode, setMode] = useState<EvaluationType>("FULL");

  // API Mutation using React Query
  const mutation = useMutation({
    mutationFn: async (data: EvaluateRequest) => {
      const response = await api.post<EvaluateResponse>(
        "/grammar/evaluate",
        data,
      );
      return response.data;
    },
  });

  const handleCheck = () => {
    if (!text.trim()) return;
    mutation.mutate({ sentence: text, evaluationType: mode });
  };

  const result = mutation.data;

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* --- Header Section --- */}
      <div>
        <h1 className="text-3xl font-bold text-dark-900 mb-2">Grammar Check</h1>
        <p className="text-gray-500">
          Paste your text below and let our AI polish your writing.
        </p>
      </div>

      {/* --- Input Section --- */}
      <div className="bg-white rounded-2xl shadow-soft p-6 space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type or paste your English text here..."
          className="w-full h-40 p-4 rounded-xl border border-gray-200 bg-white text-dark-800 focus:border-secondary focus:ring-2 focus:ring-secondary/20 resize-none transition-all outline-none text-lg placeholder:text-gray-300"
        />

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          {/* Mode Toggle */}
          <div className="flex bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setMode("FULL")}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
                mode === "FULL"
                  ? "bg-white text-dark-900 shadow-sm"
                  : "text-gray-500 hover:text-dark-900"
              }`}
            >
              <FileText size={16} /> Detailed Analysis
            </button>
            <button
              onClick={() => setMode("QUICK")}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
                mode === "QUICK"
                  ? "bg-white text-dark-900 shadow-sm"
                  : "text-gray-500 hover:text-dark-900"
              }`}
            >
              <Zap size={16} /> Quick Check
            </button>
          </div>

          {/* Action Button */}
          <button
            onClick={handleCheck}
            disabled={mutation.isPending || !text.trim()}
            className="w-full sm:w-auto px-8 py-3 bg-primary hover:bg-primary-hover text-white rounded-xl font-semibold shadow-lg shadow-primary/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="animate-spin" /> Analyzing...
              </>
            ) : (
              <>
                Check Grammar <ArrowRight size={18} />
              </>
            )}
          </button>
        </div>
      </div>

      {/* --- Error Display --- */}
      {mutation.isError && (
        <div className="p-4 rounded-xl bg-red-50 text-red-700 border border-red-200 flex items-center gap-3 animate-fade-in">
          <XCircle size={24} />
          <span className="font-medium">
            Something went wrong while analyzing your text. Please try again
            later.
          </span>
        </div>
      )}

      {/* --- Results Section --- */}
      {result && (
        <div className="space-y-6 animate-fade-in">
          {/* 1. Verdict Banner */}
          <div
            className={`p-4 rounded-xl flex items-center gap-3 ${
              result.isCorrect
                ? "bg-green-50 text-green-700 border border-green-200"
                : "bg-red-50 text-red-700 border border-red-200"
            }`}
          >
            {result.isCorrect ? (
              <CheckCircle2 size={24} />
            ) : (
              <XCircle size={24} />
            )}
            <span className="font-medium text-lg">
              {result.isCorrect
                ? "Perfect! No errors found."
                : "Found some issues in your text."}
            </span>
          </div>

          {!result.isCorrect && (
            <div className="grid md:grid-cols-2 gap-6">
              {/* 2. Correction Card */}
              <div className="bg-white rounded-2xl shadow-soft p-6 border-l-4 border-green-500">
                <h3 className="text-gray-400 uppercase text-xs font-bold tracking-wider mb-4">
                  Corrected Version
                </h3>
                <p className="text-xl text-dark-900 font-medium leading-relaxed">
                  {result.evaluation.corrected}
                </p>
                <div className="mt-6 pt-6 border-t border-gray-100">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-xs font-bold">
                    Topic: {result.evaluation.grammarTopic}
                  </span>
                </div>
              </div>

              {/* 3. Feedback & Examples Card */}
              <div className="bg-white rounded-2xl shadow-soft p-6">
                <h3 className="text-gray-400 uppercase text-xs font-bold tracking-wider mb-4">
                  Why is this wrong?
                </h3>

                <div className="space-y-4">
                  {result.examples.map((ex, idx) => (
                    <div key={idx} className="group">
                      <div className="flex items-start gap-3">
                        <div className="mt-1 min-w-[24px] h-6 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-xs font-bold">
                          {idx + 1}
                        </div>
                        <div>
                          <p className="text-dark-800 font-medium italic">
                            "{ex.text}"
                          </p>
                          <p className="text-gray-500 text-sm mt-1">
                            {ex.explanation}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Call to Action for Exercises */}
                {result.exercises.length > 0 && (
                  <div className="mt-8 pt-6 border-t border-gray-100">
                    <button className="w-full py-2.5 rounded-lg border-2 border-primary text-primary hover:bg-primary-light font-medium transition-all flex items-center justify-center gap-2">
                      <BookOpen size={18} />
                      Practice Related Exercises
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
