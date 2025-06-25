import React, { useRef, useState } from 'react';

export default function SelfieCapture({ sessionId, onSuccess }) {
  const [preview, setPreview] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const video = useRef(), canvas = useRef();

  const startCam = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.current.srcObject = stream;
  };

  const capture = () => {
    const v = video.current, c = canvas.current;
    c.width = v.videoWidth;
    c.height = v.videoHeight;
    c.getContext('2d').drawImage(v, 0, 0);
    c.toBlob(upload, 'image/jpeg');
  };

  const upload = async blob => {
    setLoading(true);
    setPreview(URL.createObjectURL(blob));
    const file = new File([blob], 'selfie.jpg');
    const form = new FormData();
    form.append('file', file);
    form.append('session_id', sessionId);
    const res = await fetch('/upload-selfie', { method: 'POST', body: form });
    const data = await res.json();
    setLoading(false);

    if (res.ok) onSuccess();
    else setFeedback({ type: 'error', message: data.error });
  };

  return (
    <div className="card">
      <h2>Capture Selfie</h2>
      {!preview ? (
        <>
          <video ref={video} autoPlay />
          <div>
            <button className="button" onClick={startCam}>Start Camera</button>
            <button className="button" onClick={capture}>Capture</button>
          </div>
        </>
      ) : (
        <>
          <img src={preview} className="preview-image" />
        </>
      )}
      {loading && <div className="loader" />}
      {feedback && <div className={`feedback ${feedback.type}`}>{feedback.message}</div>}
      <canvas ref={canvas} className="hidden" />
    </div>
  );
}
