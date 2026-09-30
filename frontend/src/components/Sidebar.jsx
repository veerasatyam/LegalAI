import React from 'react';
import { Plus, Trash2, MessageSquare, BookOpen } from 'lucide-react';

export default function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  user
}) {
  return (
    <aside className="sidebar">
      <div>
        <button onClick={onNewSession} className="btn btn-primary btn-block">
          <Plus size={16} /> New Legal Inquiry
        </button>

        <div className="sidebar-heading">Your Inquiry Sessions</div>

        <div className="sessions-scroll">
          {!user ? (
            <div className="sidebar-notice">
              Sign in to save, organize, and revisit multiple inquiry sessions in your NoSQL account.
            </div>
          ) : sessions.length === 0 ? (
            <div className="sidebar-notice">
              No sessions recorded yet. Start by describing an incident on the right.
            </div>
          ) : (
            sessions.map((sess) => (
              <div
                key={sess.id}
                className={`session-card ${sess.id === activeSessionId ? 'active' : ''}`}
                onClick={() => onSelectSession(sess.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <MessageSquare size={14} color="#64748b" />
                  <span className="session-name" title={sess.title}>
                    {sess.title}
                  </span>
                </div>
                <button
                  className="btn-del-session"
                  title="Delete session"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(sess.id);
                  }}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="sidebar-notice">
        <strong>
          <BookOpen size={13} style={{ display: 'inline', marginRight: '4px' }} />
          Indian Penal Code, 1860
        </strong>
        <p>463 bare act sections indexed in Chroma Cloud for semantic fact-to-law retrieval.</p>
      </div>
    </aside>
  );
}
