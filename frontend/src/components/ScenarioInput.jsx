import React from 'react';
import { Send, Sparkles, AlertCircle } from 'lucide-react';

const EXAMPLES = [
  {
    icon: '🚴',
    label: 'Bike stopped on road',
    text: 'Someone stopped my bike in the middle of the road and threatened to hit me.'
  },
  {
    icon: '🚪',
    label: 'Blocked entrance & extortion',
    text: 'A group of men blocked my house entrance and said I cannot leave until I pay them money.'
  },
  {
    icon: '🚗',
    label: 'Car damaged with stone',
    text: 'Someone broke my car window with a stone while I was driving and ran away.'
  },
  {
    icon: '💎',
    label: 'House trespass & theft',
    text: 'They entered my house at night without permission and took my jewelry and phone.'
  }
];

export default function ScenarioInput({
  input,
  setInput,
  onSubmit,
  loading
}) {
  return (
    <>
      <div className="examples-bar">
        <div className="examples-title">
          <Sparkles size={14} style={{ display: 'inline', marginRight: '5px' }} />
          Common real-life incidents to explore:
        </div>
        <div className="chips-row">
          {EXAMPLES.map((ex, idx) => (
            <button
              key={idx}
              className="example-chip"
              onClick={() => setInput(ex.text)}
              type="button"
            >
              <span style={{ marginRight: '6px' }}>{ex.icon}</span>
              {ex.label}
            </button>
          ))}
        </div>
      </div>

      <div className="input-panel">
        <div className="input-header">
          <span className="input-title">Describe Your Real-Life Situation</span>
          <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Everyday natural language</span>
        </div>

        <textarea
          className="scenario-textarea"
          rows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Example: Someone intentionally stood in front of my vehicle, refused to move, and threatened to harm me if I passed through the public road..."
        />

        <div className="input-actions">
          <span className="input-subtext">
            💡 Provide details about actions, location, and whether threats or property harm occurred.
          </span>
          <button
            onClick={onSubmit}
            disabled={loading || !input.trim()}
            className="btn btn-primary btn-large"
          >
            {loading ? (
              <>
                <span className="badge-dot" style={{ background: 'white' }}></span> Analyzing Law...
              </>
            ) : (
              <>
                <Send size={16} /> Analyze Legal Scenario
              </>
            )}
          </button>
        </div>
      </div>

      {loading && (
        <div className="pipeline-stepper">
          <div className="stepper-bar"></div>
          <div className="stepper-labels">
            <span>1. Intent & Safety Classification</span>
            <span>2. Legal Fact Extraction</span>
            <span>3. Chroma Cloud Semantic Search</span>
            <span>4. Grok Legal Reasoning</span>
          </div>
        </div>
      )}
    </>
  );
}
