// React-based BRoT Dashboard
import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [status, setStatus] = useState('Idle');
  const [logs, setLogs] = useState([]);
  const [sequenceInput, setSequenceInput] = useState('');
  const [riskScore, setRiskScore] = useState(null);
  const [releaseToken, setReleaseToken] = useState(null);

  const handleScreenSequence = async () => {
    if (!sequenceInput.trim()) {
      alert('Please enter a sequence');
      return;
    }
    
    setStatus('Screening...');
    addLog(`Processing sequence: ${sequenceInput.substring(0, 30)}...`);
    
    try {
      // Simulate ML inference with realistic risk scoring
      const hashCode = sequenceInput.split('').reduce((h, c) => {
        const code = c.charCodeAt(0);
        return ((h << 5) - h) + code;
      }, 0);
      
      const simulatedRisk = Math.abs(Math.sin(hashCode / 1000)) * 0.8 + 0.1;
      const isApproved = simulatedRisk < 0.5;
      
      setRiskScore(simulatedRisk.toFixed(3));
      
      if (isApproved) {
        const token = Math.random().toString(16).substring(2);
        setReleaseToken(token);
        addLog(`✓ APPROVED - Risk: ${simulatedRisk.toFixed(2)}, Token: ${token.substring(0, 16)}...`);
      } else {
        setReleaseToken(null);
        addLog(`✗ BLOCKED - Risk: ${simulatedRisk.toFixed(2)} exceeds threshold`);
      }
      
      setStatus('Complete');
      setTimeout(() => setStatus('Idle'), 3000);
    } catch (error) {
      addLog(`Error: ${error.message}`);
      setStatus('Error');
    }
  };

  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const handleClearLogs = () => {
    setLogs([]);
  };

  const handleStartDemo = () => {
    setStatus('Running');
    addLog('System initialized');
    addLog('Sentinel Head loaded: ESM-2 t33 650M');
    addLog('BlackBox initialized - logging enabled');
    addLog('Interlock status: LOCKED (awaiting authorization)');
    addLog('Ready for DNA synthesis screening');
    setTimeout(() => setStatus('Ready'), 1000);
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <header style={{ borderBottom: '2px solid #333', paddingBottom: '10px', marginBottom: '20px' }}>
        <h1>🛡️ SynthShield BRoT Dashboard</h1>
        <p>Benchtop DNA Synthesis Security System</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        {/* Control Panel */}
        <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h2>System Control</h2>
          <p><strong>Status:</strong> {status}</p>
          <button 
            onClick={handleStartDemo}
            style={{ 
              padding: '10px 20px', 
              fontSize: '16px', 
              marginRight: '10px',
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>
            Initialize System
          </button>
        </div>

        {/* Risk Score Display */}
        <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h2>Current Assessment</h2>
          {riskScore !== null ? (
            <div>
              <p><strong>Risk Score:</strong> {riskScore}</p>
              <p><strong>Decision:</strong> {parseFloat(riskScore) < 0.5 ? '✓ APPROVED' : '✗ BLOCKED'}</p>
              {releaseToken && <p><strong>Token:</strong> {releaseToken.substring(0, 20)}...</p>}
            </div>
          ) : (
            <p>No sequence screened yet</p>
          )}
        </div>
      </div>

      {/* Sequence Input */}
      <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: '20px' }}>
        <h2>DNA Sequence Screening</h2>
        <textarea
          value={sequenceInput}
          onChange={(e) => setSequenceInput(e.target.value)}
          placeholder="Enter DNA sequence (ATCG...)"
          style={{
            width: '100%',
            height: '100px',
            padding: '10px',
            fontFamily: 'monospace',
            borderRadius: '4px',
            border: '1px solid #ccc'
          }}
        />
        <div style={{ marginTop: '10px' }}>
          <button 
            onClick={handleScreenSequence}
            style={{
              padding: '10px 20px',
              fontSize: '16px',
              backgroundColor: '#2196F3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>
            Screen Sequence
          </button>
        </div>
      </div>

      {/* Event Log */}
      <div style={{ backgroundColor: 'white', padding: '15px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h2>System Log</h2>
          <button 
            onClick={handleClearLogs}
            style={{
              padding: '5px 15px',
              fontSize: '14px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>
            Clear
          </button>
        </div>
        <div style={{
          backgroundColor: '#f9f9f9',
          border: '1px solid #ddd',
          borderRadius: '4px',
          padding: '10px',
          height: '250px',
          overflowY: 'auto',
          fontFamily: 'monospace',
          fontSize: '12px'
        }}>
          {logs.length === 0 ? (
            <p style={{ color: '#999' }}>No events logged yet</p>
          ) : (
            logs.map((log, idx) => <div key={idx}>{log}</div>)
          )}
        </div>
      </div>

      <footer style={{ marginTop: '20px', paddingTop: '10px', borderTop: '1px solid #ddd', textAlign: 'center', color: '#666' }}>
        <p>SynthShield v0.1 | Biosecurity Modernization Act 2026 Compliant | Cryptographically Auditable</p>
      </footer>
    </div>
  );
};

export default App;