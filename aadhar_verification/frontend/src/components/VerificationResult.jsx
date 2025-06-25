import React, { useEffect } from 'react';

export default function VerificationResult({ sessionId, onResult }) {
  const [loading, setLoading] = React.useState(true);

  useEffect(() => {
    (async () => {
      const res = await fetch('/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      const data = await res.json();
      onResult(data);
      setLoading(false);
    })();
  }, []);

  return (
    <div className="card text-center">
      <h2>Verifying...</h2>
      {loading && <div className="loader" />}
    </div>
  );
}
