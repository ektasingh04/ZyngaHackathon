import React, { useState } from 'react';

export default function AadhaarUpload({ onSuccess }) {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const upload = async file => {
    setLoading(true);
    setFeedback(null);
    setPreview(URL.createObjectURL(file));

    const form = new FormData();
    form.append('file', file);
    const res = await fetch('/upload-aadhaar', { method: 'POST', body: form });
    const data = await res.json();
    setLoading(false);

    if (res.ok && data.session_id) onSuccess(data.session_id);
    else setFeedback({ type: 'error', message: data.error || 'Upload failed' });
  };

  return (
    <div className="card">
      <h2>Upload Aadhaar</h2>
      {!preview ? (
        <div className="upload-box">
          <p>Drag or select Aadhaar image</p>
          <label className="upload-label">
            Choose File
            <input type="file" accept="image/*" onChange={e => upload(e.target.files[0])} />
          </label>
        </div>
      ) : (
        <>
          <img src={preview} className="preview-image" />
          <button className="button" onClick={() => window.location.reload()}>Retake</button>
        </>
      )}
      {loading && <div className="loader" />}
      {feedback && <div className={`feedback ${feedback.type}`}>{feedback.message}</div>}
    </div>
  );
}
