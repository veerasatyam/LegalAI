import React from 'react';
import {
  FileText,
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  Info,
  Clock,
  CheckCircle,
  HelpCircle,
  Scale
} from 'lucide-react';

export default function ResultsView({ result }) {
  if (!result) return null;

  const sections = result.legal_analysis?.applicable_sections || [];
  const risk = result.risk_assessment || {};
  const riskLevel = (risk.level || 'MEDIUM').toUpperCase();

  const getRiskIcon = (lvl) => {
    if (lvl === 'HIGH') return <ShieldAlert size={20} color="#b91c1c" />;
    if (lvl === 'MEDIUM') return <AlertTriangle size={20} color="#b45309" />;
    return <ShieldCheck size={20} color="#047857" />;
  };

  return (
    <div className="results-stack">
      {/* Summary Card */}
      <div className="summary-card">
        <div className="summary-top">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={18} color="#1e3a8a" />
            <h3 className="summary-heading">Scenario Summary & Legal Evaluation</h3>
          </div>
          <span className="time-pill">
            <Clock size={12} style={{ display: 'inline', marginRight: '4px' }} />
            {result.processing_time_ms || 240}ms
          </span>
        </div>
        <p className="summary-body">{result.summary}</p>
      </div>

      {/* Sections Grid */}
      <div>
        <div className="sections-header">
          <h3 className="sections-heading">
            <Scale size={20} style={{ display: 'inline', marginRight: '6px' }} />
            Applicable Indian Penal Code (IPC) Sections
          </h3>
          <p className="sections-sub">
            Provisions matched against the factual ingredients of the scenario
          </p>
        </div>

        {sections.length === 0 ? (
          <div className="ipc-card">
            <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
              No specific statutory sections matched with sufficient confidence. Please provide additional details or consult a legal practitioner.
            </p>
          </div>
        ) : (
          <div className="sections-deck">
            {sections.map((sec, idx) => {
              const conf = sec.confidence || 'MEDIUM';
              return (
                <div key={idx} className="ipc-card">
                  <div>
                    <div className="ipc-top">
                      <span className="ipc-num">{sec.section}</span>
                      <span className={`confidence-tag conf-${conf}`}>
                        {conf} Match
                      </span>
                    </div>

                    <h4 className="ipc-title">{sec.title}</h4>

                    <p className="ipc-meaning">
                      {sec.plain_meaning || sec.explanation || sec.summary}
                    </p>

                    {sec.why_applies && sec.why_applies.length > 0 && (
                      <div className="ipc-why">
                        <strong>Why this provision applies:</strong>
                        {sec.why_applies.map((reason, rIdx) => (
                          <div key={rIdx}>• {reason}</div>
                        ))}
                      </div>
                    )}
                  </div>

                  {sec.punishment && (
                    <div className="ipc-punishment">
                      ⚖️ <strong>Punishment:</strong> {sec.punishment}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Risk Alert */}
      <div className={`risk-card risk-${riskLevel}`}>
        <div className="risk-top">
          {getRiskIcon(riskLevel)}
          <span>{riskLevel} LEGAL SEVERITY & RISK</span>
        </div>
        <p className="risk-body">
          {risk.advice || risk.reason || 'Exercise caution and document all relevant facts.'}
        </p>
      </div>

      {/* Practical Guidance Matrix */}
      <div className="guidance-matrix">
        <div className="guidance-box">
          <h4>🚨 Immediate Actions</h4>
          <ul className="guidance-items">
            {(result.practical_guidance?.immediate_actions || [
              'Ensure physical safety first',
              'Dial police control room (100) if threatened'
            ]).map((act, i) => (
              <li key={i}>{act}</li>
            ))}
          </ul>
        </div>

        <div className="guidance-box">
          <h4>⚖️ Legal Steps</h4>
          <ul className="guidance-items">
            {(result.practical_guidance?.legal_steps || result.next_steps || [
              'Visit nearest jurisdictional police station',
              'Request copy of written complaint / FIR'
            ]).map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ul>
        </div>

        <div className="guidance-box">
          <h4>📸 Evidence Checklist</h4>
          <ul className="guidance-items">
            {(result.practical_guidance?.evidence_to_collect || [
              'Photographs or video of the location',
              'Contact details of eyewitnesses'
            ]).map((ev, i) => (
              <li key={i}>{ev}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Warnings if any */}
      {result.warnings && result.warnings.length > 0 && (
        <div
          style={{
            background: '#fff7ed',
            border: '1px solid #fed7aa',
            borderRadius: '12px',
            padding: '1rem',
            color: '#9a3412'
          }}
        >
          <strong style={{ display: 'block', marginBottom: '6px' }}>
            ⚠️ Important Legal Warnings:
          </strong>
          <ul style={{ paddingLeft: '18px', fontSize: '0.86rem' }}>
            {result.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Statutory Disclaimer */}
      <div className="disclaimer-card">
        <Info size={20} color="#64748b" style={{ flexShrink: 0 }} />
        <p>
          <strong>Statutory Legal Notice:</strong> {result.disclaimer || 'This platform provides legal awareness for educational purposes and does not constitute formal legal advice or attorney representation.'}
        </p>
      </div>
    </div>
  );
}
