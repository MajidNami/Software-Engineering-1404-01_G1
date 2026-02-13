// src/types/api.ts

// --- Constants & Types (Replaces Enums for modern TS/Vite compatibility) ---

export type EvaluationType = "FULL" | "QUICK";

export type GrammarLevel = "EASY" | "MEDIUM" | "HARD";

export type ExerciseType = "FILL_BLANK" | "MULTIPLE_CHOICE" | "FULL_SENTENCE";

export type GrammarTopic =
  // TENSE
  | "PRESENT_SIMPLE"
  | "PRESENT_CONTINUOUS"
  | "PAST_SIMPLE"
  | "PAST_CONTINUOUS"
  | "PRESENT_PERFECT"
  | "PAST_PERFECT"
  | "TENSE_CHOICE"
  // CONDITIONAL
  | "CONDITIONAL_ZERO"
  | "CONDITIONAL_FIRST"
  | "CONDITIONAL_SECOND"
  | "CONDITIONAL_THIRD"
  | "CONDITIONAL_MIXED"
  | "WISH_IF_ONLY"
  // MODAL
  | "MODAL_ABILITY_PERMISSION"
  | "MODAL_OBLIGATION"
  | "MODAL_POSSIBILITY"
  | "MODAL_PERFECT"
  // VOICE
  | "PASSIVE_VOICE"
  | "CAUSATIVE_HAVE_GET"
  | "REPORTED_SPEECH"
  // VERB_PATTERN
  | "GERUND_INFINITIVE"
  | "RELATIVE_CLAUSES"
  // COMPARISON
  | "ARTICLES"
  | "COMPARISON";

// --- Auth Types ---
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email: string;
}

export interface LoginResponse {
  token: string;
}

export interface User {
  id: string; // Extracted from JWT
  username: string;
}

// --- Grammar Check Types ---
export interface EvaluateRequest {
  sentence: string;
  evaluationType: EvaluationType;
}

export interface Example {
  text: string;
  explanation: string;
}

export interface Exercise {
  id: number;
  grammarTopic: GrammarTopic;
  grammarLevel: GrammarLevel;
  exerciseType: ExerciseType;
  question: string;
  options: string[]; // For Multiple Choice or Fill Blank
}

export interface GrammarEvaluation {
  original: string;
  corrected: string;
  grammarTopic: GrammarTopic;
}

export interface EvaluateResponse {
  isCorrect: boolean;
  evaluation: GrammarEvaluation;
  examples: Example[];
  exercises: Exercise[];
}

// --- Stats Types ---
export interface UserStats {
  grammarTopic: GrammarTopic;
  grammarLevel: GrammarLevel;
  sentEvaluations: number;
  correctEvaluations: number;
  seenExamples: number;
  attemptedExercises: number;
  correctExercises: number;
}
