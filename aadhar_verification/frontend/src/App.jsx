import React, { useState } from 'react';
import AadhaarUpload from './components/AadhaarUpload';
import SelfieCapture from './components/SelfieCapture';
import VerificationResult from './components/VerificationResult';

export default function App() {
  const [step, setStep] = useState(1);
  const [sessionId, setSessionId] = useState(null);
  const [result, setResult] = useState(null);

  return (
    <div className="container">
      <h1>Aadhaar Age & Identity Verification</h1>
      {step === 1 && (
        <AadhaarUpload onSuccess={id => { setSessionId(id); setStep(2); }} />
      )}
      {step === 2 && (
        <SelfieCapture sessionId={sessionId} onSuccess={() => setStep(3)} />
      )}
      {step === 3 && (
        <VerificationResult sessionId={sessionId} onResult={res => { setResult(res); setStep(4); }} />
      )}
      {step === 4 && result && (
        <div className="card">
          <h2>Results</h2>
          <pre>{JSON.stringify(result, null, 2)}</pre>
          <button className="button" onClick={() => window.location.reload()}>
            Restart
          </button>
        </div>
      )}
    </div>
  );
}
