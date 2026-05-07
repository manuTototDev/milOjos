'use client';
import { useRef, useState, useEffect, useCallback } from 'react';
import styles from './page.module.css';

const API          = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const INTERVAL_MS  = 800;
const HISTORY_SIZE = 12;
const STICKY_THRESH = 6;
const ZOOM          = 1.28;

// ── Tipos ──────────────────────────────────────────────────────────────────────
interface FaceBox { x: number; y: number; w: number; h: number; lm106?: Pt[]; }
interface Pt      { x: number; y: number; }
interface Match   { id: number; name: string; year: string; foto: string; boletin: string; score: number; match_face_box?: FaceBox | null; }
interface Visitor { gender: string; age: number; }
interface ServoStatus { connected: boolean; port: string; active_arms: number[]; positions: number[][]; }

// ── Landmark groups ────────────────────────────────────────────────────────────
function seqLines(s: number, e: number): [number,number][] {
  return Array.from({ length: e - s }, (_, i) => [s + i, s + i + 1]);
}
const LM_GROUPS: [number,number][][] = [
  seqLines(0,10), seqLines(10,20), seqLines(20,32),
  seqLines(33,42), seqLines(43,52), seqLines(53,63),
  seqLines(63,73), seqLines(74,84), seqLines(84,95), seqLines(96,104),
];

// ── object-fit:cover correction ────────────────────────────────────────────────
function toCover(nx: number, ny: number, vw: number, vh: number, cw: number, ch: number) {
  if (!vw || !vh || !cw || !ch) return { x: nx * cw, y: ny * ch };
  const s = Math.max(cw / vw, ch / vh);
  const rendW = vw * s; const rendH = vh * s;
  const offX  = (cw - rendW) / 2; const offY = (ch - rendH) / 2;
  return { x: nx * rendW + offX, y: ny * rendH + offY };
}

function Clock() {
  const [t, setT] = useState('');
  useEffect(() => {
    const tick = () => setT(new Date().toLocaleTimeString('es-MX', { hour12: false }));
    tick(); const id = setInterval(tick, 1000); return () => clearInterval(id);
  }, []);
  return <span>{t}</span>;
}

function AnimatedScore({ value, color }: { value: number; color: string }) {
  const [display, setDisplay] = useState(0);
  const rafRef   = useRef<number>(0);
  const startRef = useRef<number>(0);
  const fromRef  = useRef<number>(0);

  useEffect(() => {
    fromRef.current  = display;
    startRef.current = performance.now();
    const duration = 600;
    const animate = (now: number) => {
      const elapsed = now - startRef.current;
      const t = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(fromRef.current + (value - fromRef.current) * eased);
      if (t < 1) rafRef.current = requestAnimationFrame(animate);
    };
    rafRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(rafRef.current);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return <span className={styles.matchScore} style={{ color }}>{display.toFixed(1)}%</span>;
}

function MatchLandmarkOverlay({ active, delay, faceBox }: { active: boolean; delay: number; faceBox?: FaceBox | null }) {
  const [phase, setPhase]     = useState(0);
  const [groupIdx, setGroupIdx] = useState(0);

  useEffect(() => {
    if (!active) { setPhase(0); setGroupIdx(0); return; }
    const t1 = setTimeout(() => setPhase(1), delay);
    const t2 = setTimeout(() => setPhase(2), delay + 1200);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [active, delay]);

  useEffect(() => {
    if (phase !== 1 && phase !== 2) return;
    const id = setInterval(() => setGroupIdx(g => (g + 1) % LM_GROUPS.length), 400);
    return () => clearInterval(id);
  }, [phase]);

  if (phase === 0) return null;
  const lm = faceBox?.lm106 ?? [];
  const hasLandmarks = lm.length >= 106;
  const currentLines = hasLandmarks ? LM_GROUPS[groupIdx] : [];

  return (
    <svg className={styles.faceScanSvg} viewBox="0 0 100 100" preserveAspectRatio="none">
      {hasLandmarks && currentLines.map(([a, b], i) => {
        const ax = lm[a].x * 100, ay = lm[a].y * 100;
        const bx = lm[b].x * 100, by = lm[b].y * 100;
        return (
          <line key={`${groupIdx}-${i}`} x1={ax} y1={ay} x2={bx} y2={by}
            stroke="#00ff88" strokeWidth="0.6"
            opacity={phase === 1 ? 0.8 : 0.35}
            strokeDasharray={phase === 1 ? '2 3' : 'none'}
            className={phase === 1 ? styles.scanLineAnim : ''}
            style={{ animationDelay: `${i * 30}ms` }}>
            {phase === 1 && <animate attributeName="opacity" from="0" to="0.8" dur="0.15s" fill="freeze"/>}
          </line>
        );
      })}
      {hasLandmarks && phase === 2 && lm.map((pt, i) => (
        <circle key={`d-${i}`} cx={pt.x * 100} cy={pt.y * 100} r="0.35" fill="#00ff88" opacity="0.2"/>
      ))}
      {phase === 1 && (
        <line x1="5" x2="95" className={styles.scanBeam}
          stroke="#00ff88" strokeWidth="0.3" opacity="0.4"/>
      )}
    </svg>
  );
}

function MatchCardItem({ match, index, scanReveal }: { match: Match; index: number; scanReveal: number }) {
  const [loaded, setLoaded] = useState(false);
  const [hash, setHash]     = useState('0x000000');

  useEffect(() => {
    if (loaded) return;
    const interval = setInterval(() => {
      setHash('0x' + Math.random().toString(16).substring(2, 8).toUpperCase());
    }, 60);
    return () => clearInterval(interval);
  }, [loaded]);

  const src = match.foto.startsWith('http') ? match.foto : `${API}${match.foto}`;

  return (
    <div className={styles.matchCard} id={`match-card-${index}`}>
      <img src={src} alt={match.name} className={styles.matchImg}
        onLoad={() => setLoaded(true)} style={{ opacity: loaded ? 1 : 0 }} />
      {!loaded ? (
        <div className={styles.calculatingState}>
          <div className={styles.calcScanLine}/>
          <span className={styles.calcTitle}>BUSCANDO_COINCIDENCIA</span>
          <span className={styles.calcSub}>CALCULANDO...</span>
          <span className={styles.calcHash}>{hash}</span>
        </div>
      ) : (
        <>
          <MatchLandmarkOverlay active={scanReveal > 0} delay={index * 150} faceBox={match.match_face_box} key={`scan-${scanReveal}-${index}`}/>
          <div className={styles.matchOverlay}>
            <span className={styles.matchRank}>{String(index + 1).padStart(2, '0')}</span>
            <AnimatedScore value={match.score} color={match.score > 60 ? '#00ff88' : match.score > 40 ? '#ffb800' : 'rgba(255,255,255,0.4)'}/>
          </div>
          <div className={styles.matchLabel}>
            <span className={styles.matchName}>{match.name}</span>
            <span className={styles.matchYear}>{match.year}</span>
          </div>
        </>
      )}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════════
export default function EscaneoPage() {
  const videoRef   = useRef<HTMLVideoElement>(null);
  const captureRef = useRef<HTMLCanvasElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const historyRef  = useRef<number[]>([]);

  const [streaming, setStreaming]   = useState(false);
  const [matches, setMatches]       = useState<Match[]>([]);
  const [visitor, setVisitor]       = useState<Visitor | null>(null);
  const [faceBox, setFaceBox]       = useState<FaceBox | null>(null);
  const [lm106, setLm106]           = useState<Pt[]>([]);
  const [lmGroup, setLmGroup]       = useState(0);
  const [dims, setDims]             = useState({ vw: 0, vh: 0, cw: 0, ch: 0 });
  const [status, setStatus]         = useState<'idle'|'scanning'|'analyzing'|'no-face'|'error'>('idle');
  const [frameN, setFrameN]         = useState(0);
  const [scanReveal, setScanReveal] = useState(0);
  const [dbCount, setDbCount]       = useState<number | null>(null);
  const [servoStatus, setServoStatus] = useState<ServoStatus | null>(null);

  // ── DB count ──────────────────────────────────────────────────────────────
  useEffect(() => {
    fetch(`${API}/`)
      .then(r => r.json())
      .then(d => { setDbCount(d.con_foto ?? d.personas); setServoStatus(d.servos); })
      .catch(() => {});
  }, []);

  // ── Servo status polling (cada 3s) ────────────────────────────────────────
  useEffect(() => {
    const id = setInterval(() => {
      fetch(`${API}/servo/status`).then(r => r.json()).then(setServoStatus).catch(() => {});
    }, 3000);
    return () => clearInterval(id);
  }, []);

  // ── Scan animation ────────────────────────────────────────────────────────
  useEffect(() => {
    if (!matches.length) return;
    const id = setInterval(() => setScanReveal(r => r + 1), 3000);
    return () => clearInterval(id);
  }, [matches.length]);

  // ── Landmark cycling ──────────────────────────────────────────────────────
  useEffect(() => {
    if (!lm106.length) return;
    const id = setInterval(() => setLmGroup(g => (g + 1) % LM_GROUPS.length), 450);
    return () => clearInterval(id);
  }, [lm106.length]);

  // ── Dimensiones wrapper ───────────────────────────────────────────────────
  const updateDims = useCallback(() => {
    const vid = videoRef.current; const wrp = wrapperRef.current;
    if (!vid || !wrp) return;
    setDims({ vw: vid.videoWidth, vh: vid.videoHeight, cw: wrp.clientWidth, ch: wrp.clientHeight });
  }, []);

  useEffect(() => {
    if (!streaming) return;
    videoRef.current?.addEventListener('loadedmetadata', updateDims);
    updateDims();
    window.addEventListener('resize', updateDims);
    return () => window.removeEventListener('resize', updateDims);
  }, [streaming, updateDims]);

  // ── Cámara ────────────────────────────────────────────────────────────────
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setStreaming(true);
        setStatus('scanning');
      }
    } catch { setStatus('error'); }
  }, []);

  // ── Análisis de frame ─────────────────────────────────────────────────────
  const analyzeFrame = useCallback(async () => {
    const vid = videoRef.current; const cvs = captureRef.current;
    if (!vid || !cvs || vid.readyState < 2) return;
    cvs.width  = vid.videoWidth  || 640;
    cvs.height = vid.videoHeight || 480;
    cvs.getContext('2d')!.drawImage(vid, 0, 0);
    setFrameN(n => n + 1);

    cvs.toBlob(async (blob) => {
      if (!blob) return;
      setStatus('analyzing');
      try {
        const fd = new FormData();
        fd.append('file', blob, 'f.jpg');
        const res = await fetch(`${API}/search`, { method: 'POST', body: fd });

        if (res.status === 422) {
          setStatus('no-face');
          setFaceBox(null);
          setLm106([]);
          // Notificar al backend que no hay rostro
          fetch(`${API}/servo/no-face`, { method: 'POST' }).catch(() => {});
          return;
        }
        if (!res.ok) { setStatus('error'); return; }

        const data = await res.json();
        setVisitor(data.visitor);
        setFaceBox(data.face_box ?? null);
        setLm106(data.lm106 ?? []);

        // ── Enviar face_box a los servos ──────────────────────────────────
        if (data.face_box) {
          fetch(`${API}/servo/track`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              ...data.face_box,
              img_w: cvs.width,
              img_h: cvs.height,
            }),
          }).catch(() => {});
        }

        // ── Sticky logic ──────────────────────────────────────────────────
        const bestId = data.results[0]?.id ?? -1;
        historyRef.current.push(bestId);
        if (historyRef.current.length > HISTORY_SIZE) historyRef.current.shift();
        const cnt: Record<number,number> = {};
        historyRef.current.forEach(id => { cnt[id] = (cnt[id]||0)+1; });
        const [domId, domCnt] = Object.entries(cnt).sort((a,b) => +b[1] - +a[1])[0];
        if (!matches.length || (+domId !== matches[0].id && domCnt >= STICKY_THRESH)) {
          setMatches(data.results);
          setScanReveal(r => r + 1);
        }
        setStatus('scanning');
      } catch { setStatus('error'); }
    }, 'image/jpeg', 0.8);
  }, [matches]);

  useEffect(() => {
    if (streaming) intervalRef.current = setInterval(analyzeFrame, INTERVAL_MS);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [streaming, analyzeFrame]);

  // ── Zoom centrado en rostro ───────────────────────────────────────────────
  const { vw, vh, cw, ch } = dims;
  const zoomOrigin = (() => {
    if (!faceBox || !vw) return '50% 50%';
    const mx = 1 - (faceBox.x + faceBox.w / 2);
    const my = faceBox.y + faceBox.h / 2;
    const p  = toCover(mx, my, vw, vh, cw, ch);
    return `${(p.x / cw * 100).toFixed(1)}% ${(p.y / ch * 100).toFixed(1)}%`;
  })();

  const toSVG = useCallback((nx: number, ny: number) => {
    if (!vw) return { x: 0, y: 0 };
    return toCover(1 - nx, ny, vw, vh, cw, ch);
  }, [vw, vh, cw, ch]);

  const bboxSVG = (() => {
    if (!faceBox || !vw) return null;
    const tl = toCover(1 - (faceBox.x + faceBox.w), faceBox.y,           vw, vh, cw, ch);
    const br = toCover(1 - faceBox.x,               faceBox.y + faceBox.h, vw, vh, cw, ch);
    return { x: tl.x, y: tl.y, w: br.x - tl.x, h: br.y - tl.y };
  })();

  const lines = lm106.length >= 106 ? LM_GROUPS[lmGroup] : [];

  const statusColor = { idle:'rgba(255,255,255,0.15)',scanning:'#00ff88',analyzing:'#ffb800','no-face':'rgba(255,255,255,0.2)',error:'#ff2d2d' }[status];
  const statusLabel = { idle:'INACTIVO',scanning:'ESCANEANDO',analyzing:'PROCESANDO','no-face':'SIN ROSTRO',error:'ERROR' }[status];

  // ── Datos brazo 1 para HUD ────────────────────────────────────────────────
  const arm1 = servoStatus?.positions?.[0];

  return (
    <div className={styles.root}>

      {/* ══ IZQUIERDA ══════════════════════════════ */}
      <div className={styles.left}>
        <canvas ref={captureRef} style={{ display:'none' }}/>

        <div ref={wrapperRef} className={styles.videoWrapper}
          style={{
            transformOrigin: zoomOrigin,
            transform: (faceBox && streaming) ? `scale(${ZOOM})` : 'scale(1)',
            transition: 'transform 0.7s ease, transform-origin 0.7s ease',
          }}>
          <video ref={videoRef} autoPlay muted playsInline className={styles.video}
            style={{ display: streaming ? 'block' : 'none', transform: 'scaleX(-1)' }}/>

          {streaming && vw > 0 && (
            <svg className={styles.svgOverlay} viewBox={`0 0 ${cw} ${ch}`} preserveAspectRatio="none">
              {bboxSVG && (() => {
                const { x, y, w, h } = bboxSVG;
                const C = 14;
                return (
                  <g>
                    <rect x={x} y={y} width={w} height={h} fill="none" stroke="rgba(0,255,136,0.35)" strokeWidth="1"/>
                    {[
                      `M${x},${y+C} L${x},${y} L${x+C},${y}`,
                      `M${x+w-C},${y} L${x+w},${y} L${x+w},${y+C}`,
                      `M${x+w},${y+h-C} L${x+w},${y+h} L${x+w-C},${y+h}`,
                      `M${x+C},${y+h} L${x},${y+h} L${x},${y+h-C}`,
                    ].map((d,i) => <path key={i} d={d} fill="none" stroke="#00ff88" strokeWidth="2"/>)}
                    <text x={x} y={y - 6} fill="#00ff88" fontSize="8" fontFamily="IBM Plex Mono,monospace" letterSpacing="2">
                      ANALIZANDO
                    </text>
                  </g>
                );
              })()}
              {lm106.length >= 106 && lines.map(([a, b], i) => {
                const pa = toSVG(lm106[a].x, lm106[a].y);
                const pb = toSVG(lm106[b].x, lm106[b].y);
                return (
                  <line key={`${lmGroup}-${i}`}
                    x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y}
                    stroke="#00ff88" strokeWidth="0.8" opacity="0.65" strokeDasharray="3 4">
                    <animate attributeName="opacity" from="0" to="0.65" dur="0.15s" fill="freeze"/>
                  </line>
                );
              })}
            </svg>
          )}
        </div>

        {/* Idle */}
        {!streaming && (
          <div className={styles.idle}>
            <div className={styles.crosshair}><span/><span/></div>
            <p className={styles.idleLabel}>SISTEMA EN ESPERA</p>
            <button className={styles.startBtn} onClick={startCamera} id="btn-iniciar-escaneo">
              INICIAR ESCANEO
            </button>
            <p className={styles.idleSub}>Se solicitará acceso a la cámara.<br/>Ninguna imagen se almacena.</p>
          </div>
        )}

        {/* HUD */}
        {streaming && (
          <div className={styles.hud}>
            <div className={styles.corner} data-pos="tl"/>
            <div className={styles.corner} data-pos="br"/>
            <div className={styles.hudStatus}>
              <span className={styles.dot} style={{ background: statusColor }}/>
              <span style={{ color: statusColor, fontFamily:'var(--mono)', fontSize:9, letterSpacing:'0.18em' }}>
                {statusLabel}
              </span>
            </div>
            {visitor && (
              <div className={styles.hudBio}>
                <span className={styles.dataLabel}>sexo detectado</span>
                <span>{visitor.gender.toUpperCase()}</span>
                <span className={styles.dataLabel} style={{ marginTop:6 }}>edad estimada</span>
                <span>{visitor.age} AÑOS</span>
              </div>
            )}
            <div className={styles.hudFrame}>
              <span className={styles.dataLabel}>frame</span>
              <span>{String(frameN).padStart(6,'0')}</span>
            </div>

            {/* ── Servo HUD ── */}
            <div className={styles.servoHud}>
              <span className={servoStatus?.connected ? styles.servoConnected : styles.servoSimulation}>
                {servoStatus?.connected ? `● ${servoStatus.port}` : '● SIMULACIÓN'}
              </span>
              {arm1 && (
                <>
                  <span>B:{ Math.round(arm1[0])}° H:{Math.round(arm1[1])}°</span>
                  <span>C:{Math.round(arm1[2])}° M:{Math.round(arm1[3])}°</span>
                </>
              )}
              <span style={{ color:'rgba(255,255,255,0.15)' }}>BRAZO 1 / {servoStatus?.active_arms.length ?? 1} ACTIVO(S)</span>
            </div>
          </div>
        )}

        <div className={styles.leftFooter}>
          <span className={styles.tag}>MIL OJOS — v3.0</span>
          <Clock/>
          <span className={styles.tag}>PRODUCCIÓN</span>
        </div>
      </div>

      {/* ══ DERECHA ════════════════════════════════ */}
      <div className={styles.right}>
        <div className={styles.rightHeader}>
          <div>
            <p className={styles.tag}>similitud facial / tiempo real</p>
            <h1 className={styles.rightTitle}>COINCIDENCIAS<span className={styles.cursor}>_</span></h1>
            <p className={styles.algoNote}>
              Las 8 personas de la base de datos con mayor similitud facial. El sistema captura tu imagen,
              genera un vector de 512 dimensiones con InsightFace y lo compara usando similitud coseno.
              El Brazo 1 sigue al rostro en tiempo real vía Arduino.
            </p>
          </div>
          <div className={styles.dbInfo}>
            <span className={styles.dataLabel}>base de datos</span>
            <span className={styles.dbCount}>{dbCount !== null ? dbCount.toLocaleString() : '…'}</span>
            <span className={styles.dataLabel}>personas indexadas</span>
          </div>
        </div>
        <div className={styles.divider}/>
        <div className={styles.grid} id="match-grid">
          {matches.length === 0
            ? <div className={styles.emptyState}>
                {!streaming ? 'Inicia el escaneo para ver resultados.' : 'Posicionate frente a la cámara…'}
              </div>
            : matches.slice(0,8).map((m,i) => (
                <MatchCardItem key={m.id} match={m} index={i} scanReveal={scanReveal}/>
              ))
          }
        </div>
        <div className={styles.rightFooter}>
          <a href="https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas"
            target="_blank" rel="noopener noreferrer" className={styles.footerLink} id="btn-cobupem">
            COBUPEM — SITIO OFICIAL ↗
          </a>
          <span className={styles.tag}>EDOMEX 2020–2026</span>
        </div>
      </div>
    </div>
  );
}
