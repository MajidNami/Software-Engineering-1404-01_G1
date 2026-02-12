import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-xl border border-border bg-white p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-slate-800 mb-4">TOEFL Listening</h1>
        <p className="text-slate-600 text-sm mb-6">Sign in to continue</p>
        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
        <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded-lg mb-4"
          required
        />
        <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded-lg mb-6"
          required
        />
        <button type="submit" className="w-full py-2 bg-primary text-white rounded-lg font-medium hover:bg-primary-hover">
          Sign in
        </button>
      </form>
    </div>
  );
}
