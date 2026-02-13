import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";
import {
  type UserStats,
  type GrammarLevel,
  type GrammarTopic,
} from "../types/api";
import { Filter, Target, BookOpen, PenTool } from "lucide-react";

// --- اصلاح شده: حذف FUTURE_SIMPLE از لیست ---
const TOPICS: GrammarTopic[] = [
  "PRESENT_SIMPLE",
  "PRESENT_CONTINUOUS",
  "PAST_SIMPLE",
  "PAST_CONTINUOUS",
  "PRESENT_PERFECT",
  "TENSE_CHOICE",
  "CONDITIONAL_FIRST",
  "PASSIVE_VOICE",
  "ARTICLES",
];

export default function Stats() {
  const { userId } = useAuth();
  const [selectedTopic, setSelectedTopic] =
    useState<GrammarTopic>("PRESENT_SIMPLE");
  const [selectedLevel, setSelectedLevel] = useState<GrammarLevel>("MEDIUM");

  // Fetch Stats based on filters
  const { data: stats, isLoading } = useQuery({
    queryKey: ["stats", userId, selectedTopic, selectedLevel],
    queryFn: async () => {
      const res = await api.get<UserStats>(`/users/${userId}/stats`, {
        params: {
          grammarTopic: selectedTopic,
          grammarLevel: selectedLevel,
        },
      });
      return res.data;
    },
    retry: false,
  });

  // Prepare Data for Charts
  const radarData = stats
    ? [
        { subject: "Writing Qty", A: stats.sentEvaluations, fullMark: 100 },
        {
          subject: "Writing Acc",
          A: (stats.correctEvaluations / (stats.sentEvaluations || 1)) * 100,
          fullMark: 100,
        },
        { subject: "Exercise Qty", A: stats.attemptedExercises, fullMark: 100 },
        {
          subject: "Exercise Acc",
          A: (stats.correctExercises / (stats.attemptedExercises || 1)) * 100,
          fullMark: 100,
        },
        { subject: "Examples", A: stats.seenExamples * 5, fullMark: 100 }, // Weighted
      ]
    : [];

  const barData = stats
    ? [
        {
          name: "Sentences",
          total: stats.sentEvaluations,
          correct: stats.correctEvaluations,
        },
        {
          name: "Exercises",
          total: stats.attemptedExercises,
          correct: stats.correctExercises,
        },
      ]
    : [];

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12 animate-fade-in">
      {/* --- Header & Filters --- */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-3xl font-bold text-dark-900">
            Detailed Progress
          </h1>
          <p className="text-gray-500 mt-1">
            Deep dive into your grammar skills and performance metrics.
          </p>
        </div>

        {/* Filters Card */}
        <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-200 flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2 text-gray-500 font-medium">
            <Filter size={18} /> Filters:
          </div>

          <select
            value={selectedTopic}
            onChange={(e) => setSelectedTopic(e.target.value as GrammarTopic)}
            className="px-4 py-2 rounded-xl bg-gray-50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary/20 text-sm"
          >
            {TOPICS.map((t) => (
              <option key={t} value={t}>
                {t.replace("_", " ")}
              </option>
            ))}
          </select>

          <div className="h-6 w-px bg-gray-200"></div>

          <div className="flex bg-gray-100 p-1 rounded-lg">
            {(["EASY", "MEDIUM", "HARD"] as GrammarLevel[]).map((level) => (
              <button
                key={level}
                onClick={() => setSelectedLevel(level)}
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
      </div>

      {/* --- Main Content --- */}
      {isLoading ? (
        <div className="h-64 flex items-center justify-center text-gray-400">
          Loading stats...
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: KPI Cards */}
          <div className="space-y-6">
            <KpiCard
              title="Writing Accuracy"
              value={`${Math.round((stats.correctEvaluations / (stats.sentEvaluations || 1)) * 100)}%`}
              subtext={`${stats.correctEvaluations}/${stats.sentEvaluations} Sentences correct`}
              icon={<PenTool size={20} className="text-white" />}
              color="bg-blue-500"
            />
            <KpiCard
              title="Exercise Score"
              value={`${Math.round((stats.correctExercises / (stats.attemptedExercises || 1)) * 100)}%`}
              subtext={`${stats.correctExercises}/${stats.attemptedExercises} Answers correct`}
              icon={<Target size={20} className="text-white" />}
              color="bg-green-500"
            />
            <KpiCard
              title="Learning Intensity"
              value={stats.seenExamples}
              subtext="Examples studied"
              icon={<BookOpen size={20} className="text-white" />}
              color="bg-orange-500"
            />
          </div>

          {/* Middle: Radar Chart (Skill Balance) */}
          <div className="bg-white p-6 rounded-2xl shadow-soft border border-gray-100 flex flex-col items-center justify-center">
            <h3 className="text-lg font-bold text-dark-800 mb-2">
              Skill Balance
            </h3>
            <div className="w-full h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart
                  cx="50%"
                  cy="50%"
                  outerRadius="80%"
                  data={radarData}
                >
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis
                    dataKey="subject"
                    tick={{ fill: "#6b7280", fontSize: 12 }}
                  />
                  <PolarRadiusAxis
                    angle={30}
                    domain={[0, 100]}
                    tick={false}
                    axisLine={false}
                  />
                  <Radar
                    name="Performance"
                    dataKey="A"
                    stroke="#F97316"
                    strokeWidth={3}
                    fill="#F97316"
                    fillOpacity={0.2}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-center text-gray-400 mt-4">
              Comparing quantity vs. quality across writing and exercises.
            </p>
          </div>

          {/* Right: Bar Chart (Attempts vs Success) */}
          <div className="bg-white p-6 rounded-2xl shadow-soft border border-gray-100">
            <h3 className="text-lg font-bold text-dark-800 mb-6">
              Success Rate
            </h3>
            <div className="w-full h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData} barSize={30}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} />
                  <YAxis axisLine={false} tickLine={false} />
                  <Tooltip cursor={{ fill: "#F9FAFB" }} />
                  <Bar
                    dataKey="total"
                    name="Total Attempts"
                    fill="#F3F4F6"
                    radius={[4, 4, 0, 0]}
                  />
                  <Bar
                    dataKey="correct"
                    name="Correct"
                    fill="#10B981"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
          <p className="text-gray-400">
            No stats available for this selection.
          </p>
        </div>
      )}
    </div>
  );
}

// Helper Component
function KpiCard({ title, value, subtext, icon, color }: any) {
  return (
    <div className="bg-white p-5 rounded-2xl shadow-soft border border-gray-100 flex items-center gap-4 transition-transform hover:translate-x-1">
      <div
        className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-lg shadow-gray-200 ${color}`}
      >
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-gray-400">{title}</p>
        <h4 className="text-2xl font-bold text-dark-900">{value}</h4>
        <p className="text-xs text-gray-500 mt-0.5">{subtext}</p>
      </div>
    </div>
  );
}
