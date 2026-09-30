import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ScenarioInput from './components/ScenarioInput';
import ResultsView from './components/ResultsView';
import AuthModal from './components/AuthModal';

export default function App() {
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem('legal_auth_token') || null;
    } catch {
      return null;
    }
  });

  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('legal_user');
      if (!saved || saved === 'undefined' || saved === 'null') return null;
      return JSON.parse(saved);
    } catch {
      return null;
    }
  });

  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [inputScenario, setInputScenario] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('login');

  // Load user sessions when token changes
  useEffect(() => {
    if (token) {
      loadSessions();
    } else {
      setSessions([]);
      setActiveSessionId(null);
    }
  }, [token]);

  const loadSessions = async () => {
    if (!token) return;
    try {
      const res = await fetch('/api/sessions', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setSessions(Array.isArray(data) ? data : []);
      } else if (res.status === 401) {
        // Token expired or invalid
        handleLogout();
      }
    } catch (err) {
      console.warn('Failed to load sessions:', err);
    }
  };

  const handleSelectSession = async (sessionId) => {
    setActiveSessionId(sessionId);
    try {
      const res = await fetch(`/api/sessions/${sessionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        const msgs = data.messages || [];
        if (msgs.length > 0) {
          const lastUser = msgs.filter((m) => m.role === 'user').pop();
          const lastAssistant = msgs.filter((m) => m.role === 'assistant').pop();
          if (lastUser) setInputScenario(lastUser.content);
          if (lastAssistant && lastAssistant.structured_response) {
            setResult(lastAssistant.structured_response);
          }
        } else {
          setResult(null);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleNewSession = async () => {
    if (!token) {
      setAuthModalMode('login');
      setAuthModalOpen(true);
      return;
    }

    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ title: 'New Legal Inquiry' })
      });
      if (res.ok) {
        const newSession = await res.json();
        setActiveSessionId(newSession.id);
        setInputScenario('');
        setResult(null);
        loadSessions();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this legal inquiry session?')) return;
    try {
      const res = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        if (activeSessionId === sessionId) {
          setActiveSessionId(null);
          setResult(null);
          setInputScenario('');
        }
        loadSessions();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAnalyze = async () => {
    const text = inputScenario.trim();
    if (!text) return;

    setLoading(true);
    setResult(null);

    try {
      let endpoint = '/api/query';
      const headers = { 'Content-Type': 'application/json' };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
        let currentSessId = activeSessionId;

        // Auto-create session if none selected
        if (!currentSessId) {
          const title = text.length > 40 ? text.substring(0, 40) + '...' : text;
          const sessRes = await fetch('/api/sessions', {
            method: 'POST',
            headers,
            body: JSON.stringify({ title })
          });
          if (sessRes.ok) {
            const newSess = await sessRes.json();
            currentSessId = newSess.id;
            setActiveSessionId(newSess.id);
          }
        }

        if (currentSessId) {
          endpoint = `/api/sessions/${currentSessId}/query`;
        }
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify({ query: text })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Analysis request failed');
      }

      const responseObj = data.response || data;
      setResult(responseObj);
      if (token) loadSessions();
    } catch (err) {
      alert('Error during legal analysis: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAuthSuccess = (accessToken, userProfile) => {
    setToken(accessToken);
    setUser(userProfile);
    localStorage.setItem('legal_auth_token', accessToken);
    localStorage.setItem('legal_user', JSON.stringify(userProfile));
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('legal_auth_token');
    localStorage.removeItem('legal_user');
    setActiveSessionId(null);
    setSessions([]);
  };

  return (
    <div className="app-container">
      <Navbar
        user={user}
        onOpenAuth={(mode) => {
          setAuthModalMode(mode);
          setAuthModalOpen(true);
        }}
        onLogout={handleLogout}
      />

      <div className="main-wrapper">
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
          user={user}
        />

        <main className="content-area">
          <section className="hero-box">
            <h2>Describe What Happened in Everyday Words</h2>
            <p>
              Citizens think in terms of incidents, not legal section numbers. Enter your situation below: our Groq-powered legal reasoning pipeline extracts relevant facts, queries verified IPC bare act sections from Chroma Cloud, explains the law simply, and outlines practical next steps.
            </p>
          </section>

          <ScenarioInput
            input={inputScenario}
            setInput={setInputScenario}
            onSubmit={handleAnalyze}
            loading={loading}
          />

          <ResultsView result={result} />
        </main>
      </div>

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        initialMode={authModalMode}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  );
}
