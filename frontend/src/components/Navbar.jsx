import React from 'react';
import { Scale, LogIn, UserPlus, LogOut, CheckCircle2 } from 'lucide-react';

export default function Navbar({ user, onOpenAuth, onLogout, systemHealth }) {
  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <Scale size={24} color="#1e3a8a" />
        </div>
        <div>
          <h1 className="brand-title">Smart Legal Aid</h1>
          <span className="brand-tag">AI-Powered Legal Awareness Platform (IPC & RAG)</span>
        </div>
      </div>

      <div className="system-status">
        <span className="status-badge badge-ai" title="Groq Inference Engine">
          <span className="badge-dot"></span> Groq LPU (qwen3.8)
        </span>
        <span className="status-badge badge-vector" title="Chroma Cloud Vector Database">
          <span className="badge-dot"></span> Chroma Cloud (463 IPC)
        </span>
        <span className="status-badge badge-nosql" title="NoSQL Storage">
          <span className="badge-dot"></span> NoSQL DB
        </span>
      </div>

      <div className="auth-panel">
        {user ? (
          <div className="user-tag">
            <div className="user-avatar">
              {(String(user?.full_name || user?.username || 'U')).charAt(0).toUpperCase()}
            </div>
            <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>
              {user?.full_name || user?.username || 'Citizen'}
            </span>
            <button onClick={onLogout} className="btn btn-ghost" title="Logout">
              <LogOut size={16} /> Logout
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: '8px' }}>
            <button onClick={() => onOpenAuth('login')} className="btn btn-outline">
              <LogIn size={15} /> Sign In
            </button>
            <button onClick={() => onOpenAuth('register')} className="btn btn-primary">
              <UserPlus size={15} /> Sign Up
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
