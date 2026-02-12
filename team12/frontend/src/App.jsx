import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ModeSelect } from './pages/ModeSelect';
import { AudioSetupPage } from './pages/AudioSetupPage';
import { DirectionsPage } from './pages/DirectionsPage';
import { TestSelect } from './pages/TestSelect';
import ListeningPage from './pages/ListeningPage';

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<ModeSelect />} />
      <Route path="/audio-setup" element={<AudioSetupPage />} />
      <Route path="/directions" element={<DirectionsPage />} />
      <Route path="/tests" element={<TestSelect />} />
      <Route path="/listening" element={<ListeningPage />} />
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
