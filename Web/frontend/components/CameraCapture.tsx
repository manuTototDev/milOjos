'use client';
import { useRef, useState, useCallback } from 'react';
import styles from './CameraCapture.module.css';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Visitor { gender: string; age: number; }
interface FichaResult {
  id: number; name: string; year: string;
  foto: string; boletin: string; score: number;
}
interface SearchResponse { visitor: Visitor; results: FichaResult[]; }

interface Props {
  onResults: (data: SearchResponse) => void;
  onLoading: (v: boolean) => void;
  loading: boolean;
}

export default function CameraCapture({ onResults, onLoading, loading }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [streaming, setStreaming] = useState(false);
  const [captured, setCaptured] = useState(false);
  const [error, setError] = useState('');

  const startCamera = useCallback(async () => {
    setError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setStreaming(true);
        setCaptured(false);
      }
    } catch {
      setError('No se pudo acceder a la cámara. Verifica los permisos.');
    }
  }, []);

  const capture = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d')!;
    ctx.drawImage(video, 0, 0);

    // Detener stream
    const stream = video.srcObject as MediaStream;
    stream?.getTracks().forEach(t => t.stop());
    video.srcObject = null;
    setStreaming(false);
    setCaptured(true);

    // Enviar al backend
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      onLoading(true);
      setError('');
      try {
        const fd = new FormData();
        fd.append('file', blob, 'selfie.jpg');
        const res = await fetch(`${API}/search`, { method: 'POST', body: fd });
        if (res.status === 422) { setError('No detectamos un rostro claro. Intenta de nuevo.'); setCaptured(false); onLoading(false); return; }
        if (!res.ok) throw new Error('Error del servidor');
        const data: SearchResponse = await res.json();
        onResults(data);
      } catch (e: any) {
        setError(e.message || 'Error de conexión con el servidor.');
      } finally {
        onLoading(false);
      }
    }, 'image/jpeg', 0.9);
  }, [onResults, onLoading]);

  const reset = useCallback(() => {
    setCaptured(false);
    setError('');
    startCamera();
  }, [startCamera]);

  return (
    <div className={styles.wrapper}>
      <div className="camera-wrapper">
        <video ref={videoRef} autoPlay muted playsInline style={{ display: streaming ? 'block' : 'none' }} />
        <canvas ref={canvasRef} style={{ display: captured ? 'block' : 'none' }} />

        {!streaming && !captured && (
          <div className={styles.placeholder}>
            <div className={styles.placeholderIcon}>👁</div>
            <p>Activa tu cámara para comenzar</p>
          </div>
        )}

        {streaming && (
          <div className="camera-overlay">
            <div className="camera-scan-line" />
          </div>
        )}
      </div>

      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.controls}>
        {!streaming && !captured && (
          <button id="btn-start-camera" className="btn btn-primary btn-lg" onClick={startCamera}>
            🎥 Activar Cámara
          </button>
        )}
        {streaming && (
          <button id="btn-capture" className="btn btn-primary btn-lg" onClick={capture} disabled={loading}>
            📸 Capturar y Buscar
          </button>
        )}
        {captured && !loading && (
          <button id="btn-retry" className="btn btn-ghost" onClick={reset}>
            🔄 Intentar de nuevo
          </button>
        )}
      </div>

      {loading && (
        <div className={styles.loadingState}>
          <div className="spinner" />
          <p>Analizando rasgos y buscando en la base de datos…</p>
        </div>
      )}
    </div>
  );
}
