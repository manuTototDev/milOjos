'use client';
import { useEffect, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiStatus {
  ready: boolean;
  personas: number;
  con_foto: number;
}

export default function LoadingGate({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [info, setInfo] = useState<ApiStatus | null>(null);
  const [dots, setDots] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);

  // Animate dots
  useEffect(() => {
    const id = setInterval(() => setDots(d => d.length >= 3 ? '' : d + '.'), 500);
    return () => clearInterval(id);
  }, []);

  // Poll API until ready
  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const res = await fetch(`${API}/`, { signal: AbortSignal.timeout(8000) });
        if (!res.ok) throw new Error('API not ok');
        const data = await res.json();
        if (!cancelled) {
          setInfo({ ready: true, personas: data.personas, con_foto: data.con_foto ?? data.personas });
          // Small delay for smooth transition
          setTimeout(() => {
            setFadeOut(true);
            setTimeout(() => setStatus('ready'), 600);
          }, 800);
        }
      } catch {
        if (!cancelled) {
          setAttempt(a => a + 1);
          // Retry every 3 seconds
          setTimeout(check, 3000);
        }
      }
    };
    check();
    return () => { cancelled = true; };
  }, []);

  if (status === 'ready') return <>{children}</>;

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: '#000',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: "'IBM Plex Mono', monospace",
      opacity: fadeOut ? 0 : 1,
      transition: 'opacity 0.6s ease',
    }}>
      {/* Scan line */}
      <div style={{
        position: 'absolute', left: 0, right: 0,
        height: '1px', background: 'rgba(0,255,136,0.15)',
        animation: 'loadScan 2.5s linear infinite',
      }} />

      {/* Title */}
      <h1 style={{
        fontSize: 48, fontWeight: 300,
        letterSpacing: '0.2em',
        color: '#e8e8e8',
        margin: 0, lineHeight: 1.1,
      }}>
        MIL<br />OJOS
        <span style={{ color: '#00ff88', animation: 'blink 1s step-end infinite' }}>_</span>
      </h1>

      {/* Status */}
      <div style={{
        marginTop: 40,
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', gap: 12,
      }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: info ? '#00ff88' : attempt > 2 ? '#ffb800' : 'rgba(255,255,255,0.2)',
            animation: info ? 'none' : 'pulse 1.5s ease infinite',
            display: 'block',
          }} />
          <span style={{
            fontSize: 9, letterSpacing: '0.18em',
            color: info ? '#00ff88' : 'rgba(255,255,255,0.3)',
          }}>
            {info
              ? 'SISTEMA LISTO'
              : attempt > 2
                ? `CONECTANDO AL SERVIDOR${dots}`
                : `INICIALIZANDO${dots}`
            }
          </span>
        </div>

        {info && (
          <div style={{
            display: 'flex', gap: 24,
            animation: 'fadeUp 0.4s ease forwards',
          }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 9, letterSpacing: '0.12em', color: 'rgba(255,255,255,0.2)' }}>
                BASE DE DATOS
              </div>
              <div style={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', marginTop: 2 }}>
                {info.personas.toLocaleString()}
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 9, letterSpacing: '0.12em', color: 'rgba(255,255,255,0.2)' }}>
                CON IMAGEN
              </div>
              <div style={{ fontSize: 16, color: 'rgba(255,255,255,0.8)', marginTop: 2 }}>
                {info.con_foto.toLocaleString()}
              </div>
            </div>
          </div>
        )}

        {attempt > 5 && !info && (
          <p style={{
            fontSize: 9, color: 'rgba(255,255,255,0.15)',
            letterSpacing: '0.05em', marginTop: 8,
            textAlign: 'center', maxWidth: 260,
          }}>
            El servidor puede tardar hasta 2 minutos en arrancar si estuvo inactivo.
          </p>
        )}
      </div>

      {/* Footer */}
      <div style={{
        position: 'absolute', bottom: 20,
        fontSize: 9, letterSpacing: '0.12em',
        color: 'rgba(255,255,255,0.1)',
      }}>
        EXOESQUELETO DE VIGILANCIA AFECTIVA
      </div>

      <style>{`
        @keyframes loadScan {
          0%   { top: -1px; }
          100% { top: 100%; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50%      { opacity: 1; }
        }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50%      { opacity: 0; }
        }
      `}</style>
    </div>
  );
}
