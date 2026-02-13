import { useState } from "react";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/axios";
import { type LoginResponse } from "../types/api";
import { SpellCheck, ArrowRight, Loader2 } from "lucide-react";

interface AuthFormData {
  username: string;
  password: string;
  email?: string;
}

export default function Login() {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<AuthFormData>();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (data: AuthFormData) => {
    setIsLoading(true);
    setErrorMsg("");
    try {
      const endpoint = isRegisterMode ? "/users/register" : "/users/login";
      const payload = isRegisterMode
        ? {
            username: data.username,
            password: data.password,
            email: data.email,
          }
        : { username: data.username, password: data.password };
      const response = await api.post<LoginResponse>(endpoint, payload);
      login(response.data.token);
      navigate("/");
    } catch (err: any) {
      const msg = err?.response?.data?.message;
      setErrorMsg(
        msg ||
          (isRegisterMode
            ? "Registration failed."
            : "Invalid username or password."),
      );
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegisterMode(!isRegisterMode);
    setErrorMsg("");
    reset();
  };

  return (
    <div className="min-h-screen bg-bg-main flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-soft p-8 md:p-12">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-light text-primary rounded-full mb-4">
            <SpellCheck size={32} />
          </div>
          <h1 className="text-2xl font-bold text-dark-900">
            {isRegisterMode ? "Create Account" : "Welcome Back"}
          </h1>
          <p className="text-gray-500 mt-2">
            {isRegisterMode
              ? "Sign up for GrammarAI"
              : "Sign in to GrammarAI to continue"}
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {errorMsg && (
            <div className="p-3 text-sm text-red-600 bg-red-50 rounded-lg">
              {errorMsg}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-dark-800 mb-1">
              Username
            </label>
            <input
              {...register("username", { required: "Username is required" })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-dark-800 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              placeholder="Enter your username"
            />
            {errors.username && (
              <p className="text-red-500 text-xs mt-1">
                {errors.username.message}
              </p>
            )}
          </div>

          {isRegisterMode && (
            <div>
              <label className="block text-sm font-medium text-dark-800 mb-1">
                Email
              </label>
              <input
                type="email"
                {...register("email", {
                  required: isRegisterMode ? "Email is required" : false,
                })}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-dark-800 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                placeholder="you@example.com"
              />
              {errors.email && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.email.message}
                </p>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-dark-800 mb-1">
              Password
            </label>
            <input
              type="password"
              {...register("password", { required: "Password is required" })}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-dark-800 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="text-red-500 text-xs mt-1">
                {errors.password.message}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary hover:bg-primary-hover text-white font-semibold py-3 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-primary/30"
          >
            {isLoading ? (
              <Loader2 className="animate-spin" />
            ) : (
              <>
                {isRegisterMode ? "Create Account" : "Sign In"}{" "}
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-gray-400">
          <p>
            {isRegisterMode
              ? "Already have an account?"
              : "Don't have an account?"}{" "}
            <button
              onClick={toggleMode}
              className="text-primary hover:text-primary-hover font-medium transition-colors"
            >
              {isRegisterMode ? "Sign In" : "Sign Up"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
