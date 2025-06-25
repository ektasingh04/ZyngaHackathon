import React from 'react';

export default function AgeGroupDisplay({ results, onRestart }) {
  if (!results) return null;

  return (
    <div className="card">
      <h2>Verification Summary</h2>
      <p><strong>Name:</strong> {results.personal_info?.name || '—'}</p>
      <p><strong>Age (OCR):</strong> {results.personal_info?.age || '—'}</p>
      <p><strong>Age Group:</strong> {results.age_group || '—'}</p>
      <p><strong>Face Match:</strong> {results.face_match ? '✅ Yes' : '❌ No'} ({results.face_match_confidence}%)</p>
      <p><strong>Overall Status:</strong> {results.overall_status}</p>
      <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
        <button className="button" onClick={onRestart}>Start Over</button>
      </div>
    </div>
  );
}
