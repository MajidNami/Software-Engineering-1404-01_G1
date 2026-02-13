import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";
import { type UserStats, type GrammarTopic } from "../types/api";
import {
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Clock,
  BookOpen,
} from "lucide-react";

// Map topics to display-friendly category names
const TOPIC_CATEGORIES: Record<string, GrammarTopic[]> = {
  Tenses: [
    "PRESENT_SIMPLE",
    "PRESENT_CONTINUOUS",
    "PAST_SIMPLE",
    "PAST_CONTINUOUS",
    "PRESENT_PERFECT",
    "PAST_PERFECT",
    "TENSE_CHOICE",
  ],
  Conditionals: [
    "CONDITIONAL_ZERO",
    "CONDITIONAL_FIRST",
    "CONDITIONAL_SECOND",
    "CONDITIONAL_THIRD",
    "CONDITIONAL_MIXED",
    "WISH_IF_ONLY",
  ],
  Modals: [
    "MODAL_ABILITY_PERMISSION",
    "MODAL_OBLIGATION",
    "MODAL_POSSIBILITY",
    "MODAL_PERFECT",
  ],
  "Voice & Speech": ["PASSIVE_VOICE", "CAUSATIVE_HAVE_GET", "REPORTED_SPEECH"],
  "Verb Patterns": ["GERUND_INFINITIVE", "RELATIVE_CLAUSES"],
  "Articles & Comparison": ["ARTICLES", "COMPARISON"],
};

export default function Dashboard() {
  const { userId } = useAuth();

  // Fetch all stats for this user from the new aggregate endpoint
  const { data: allStats } = useQuery({
    queryKey: ["allStats", userId],
    queryFn: async () => {
      const res = await api.get<UserStats[]>(`/users/${userId}/stats/all`);
      return res.data;
    },
    retry: false,
  });

  // Compute aggregate numbers
  const totals = (allStats || []).reduce(
    (acc, s) => ({
      sentEvaluations: acc.sentEvaluations + s.sentEvaluations,
      correctEvaluations: acc.correctEvaluations + s.correctEvaluations,
      seenExamples: acc.seenExamples + s.seenExamples,
      attemptedExercises: acc.attemptedExercises + s.attemptedExercises,
      correctExercises: acc.correctExercises + s.correctExercises,
    }),
    {
      sentEvaluations: 0,
      correctEvaluations: 0,
      seenExamples: 0,
      attemptedExercises: 0,
      correctExercises: 0,
    },
  );

  // Build chart data from real stats grouped by category
  const chartData = Object.entries(TOPIC_CATEGORIES)
    .map(([name, topics]) => {
      const categoryStats = (allStats || []).filter((s) =>
        topics.includes(s.grammarTopic),
      );
      return {
        name,
        total: categoryStats.reduce((sum, s) => sum + s.attemptedExercises, 0),
        correct: categoryStats.reduce((sum, s) => sum + s.correctExercises, 0),
      };
    })
    .filter((d) => d.total > 0 || (allStats && allStats.length > 0));

  // Find the topic with the most errors
  const topicErrorCounts = (allStats || []).map((s) => ({
    topic: s.grammarTopic,
    errors:
      s.attemptedExercises -
      s.correctExercises +
      (s.sentEvaluations - s.correctEvaluations),
  }));
  const worstTopic = topicErrorCounts.sort((a, b) => b.errors - a.errors)[0];

  const accuracyPercent =
    totals.sentEvaluations > 0
      ? Math.round((totals.correctEvaluations / totals.sentEvaluations) * 100)
      : 0;
  const exerciseAccuracy =
    totals.attemptedExercises > 0
      ? Math.round((totals.correctExercises / totals.attemptedExercises) * 100)
      : 0;
  const overallAccuracy =
    totals.sentEvaluations + totals.attemptedExercises > 0
      ? Math.round(
          ((totals.correctEvaluations + totals.correctExercises) /
            (totals.sentEvaluations + totals.attemptedExercises)) *
            100,
        )
      : 0;

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-fade-in pb-10">
      {/* 1. Header & Welcome */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-dark-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">
            Overview of your learning progress and recent activities.
          </p>
        </div>
        <div className="flex gap-3">
          <span className="px-4 py-2 bg-white rounded-lg shadow-sm text-sm text-gray-600 border border-gray-100 flex items-center gap-2">
            <Clock size={16} /> Last Login: Today
          </span>
        </div>
      </div>

      {/* 2. Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Checks"
          value={totals.sentEvaluations}
          icon={<TrendingUp size={24} className="text-blue-500" />}
          trend={
            totals.sentEvaluations > 0
              ? `${totals.sentEvaluations} sentences checked`
              : "Start checking!"
          }
        />
        <StatsCard
          title="Accuracy Rate"
          value={`${accuracyPercent}%`}
          icon={<CheckCircle2 size={24} className="text-green-500" />}
          trend={
            accuracyPercent >= 80
              ? "+Great accuracy!"
              : accuracyPercent > 0
                ? "Keep practicing"
                : "No data yet"
          }
        />
        <StatsCard
          title="Common Errors"
          value={worstTopic ? worstTopic.topic.replace(/_/g, " ") : "None yet"}
          icon={<AlertCircle size={24} className="text-orange-500" />}
          trend={
            worstTopic && worstTopic.errors > 0
              ? "Needs attention"
              : "Looking good!"
          }
        />
        <StatsCard
          title="Exercises Done"
          value={totals.attemptedExercises}
          icon={<BookOpen size={24} className="text-purple-500" />}
          trend={`${exerciseAccuracy}% correct`}
        />
      </div>

      {/* 3. Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-96">
        {/* Main Bar Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl shadow-soft border border-gray-100 flex flex-col">
          <h3 className="text-lg font-bold text-dark-800 mb-6">
            Topic Mastery
          </h3>
          <div className="flex-1 w-full min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={
                  chartData.length > 0
                    ? chartData
                    : [{ name: "No data", total: 0, correct: 0 }]
                }
                barSize={40}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#f3f4f6"
                />
                <XAxis
                  dataKey="name"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#9CA3AF" }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#9CA3AF" }}
                />
                <Tooltip
                  cursor={{ fill: "#F9FAFB" }}
                  contentStyle={{
                    borderRadius: "12px",
                    border: "none",
                    boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                  }}
                />
                <Bar
                  dataKey="total"
                  fill="#F3F4F6"
                  radius={[4, 4, 0, 0]}
                  name="Attempts"
                />
                <Bar
                  dataKey="correct"
                  fill="#3B82F6"
                  radius={[4, 4, 0, 0]}
                  name="Correct"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart Side */}
        <div className="bg-white p-6 rounded-2xl shadow-soft border border-gray-100 flex flex-col">
          <h3 className="text-lg font-bold text-dark-800 mb-6">
            Overall Accuracy
          </h3>
          <div className="flex-1 w-full min-h-[250px] relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: "Correct", value: overallAccuracy || 1 },
                    { name: "Incorrect", value: 100 - overallAccuracy || 1 },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  <Cell fill="#10B981" />
                  <Cell fill="#FEE2E2" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            {/* Center Text */}
            <div className="absolute inset-0 flex items-center justify-center flex-col pointer-events-none">
              <span className="text-3xl font-bold text-dark-900">
                {overallAccuracy}%
              </span>
              <span className="text-xs text-gray-400">Average</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper Component for Cards
function StatsCard({ title, value, icon, trend }: any) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-soft border border-gray-100 transition-transform hover:-translate-y-1">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <h4 className="text-2xl font-bold text-dark-900 mt-1">{value}</h4>
        </div>
        <div className="p-3 bg-gray-50 rounded-xl">{icon}</div>
      </div>
      <span
        className={`text-xs font-medium px-2 py-1 rounded-full ${
          trend.includes("+")
            ? "bg-green-100 text-green-700"
            : trend.includes("Needs")
              ? "bg-orange-100 text-orange-700"
              : "bg-blue-100 text-blue-700"
        }`}
      >
        {trend}
      </span>
    </div>
  );
}
