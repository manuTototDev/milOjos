'use client';
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import styles from './home.module.css';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const PARAGRAPHS = [
  'Esta página es un paralelo digital del exoesqueleto físico. Mil Ojos es una pieza de arte electrónico: un armazón de nueve cámaras móviles montadas sobre servomotores que el portador lleva alrededor de la cabeza. Cada cámara gira de forma autónoma, rastrea rostros en el entorno y los compara —en tiempo real— contra una base de datos de personas reportadas como desaparecidas en México. Esta plataforma traslada esa misma lógica al espacio remoto: a través de la cámara de tu dispositivo, cualquier persona puede convertirse en portador y activar el mismo sistema de búsqueda.',
  'La obra parte de una imposibilidad humana: reconocer, retener y cotejar los cientos de rostros de personas desaparecidas que circulan diariamente en afiches, pantallas o redes sociales. Cada cámara, cada servo, cada conexión de datos, se convierte en un ojo que no olvida, que insiste. El proyecto propone una reflexión sobre el duelo colectivo, la vigilancia afectiva y la carga que implica la memoria social —cómo el cuerpo puede ser habitado por la tecnología no como arma, sino como órgano de búsqueda.',
  'La web extiende los ojos del exoesqueleto más allá del espacio físico. Cada visitante se convierte en portador remoto; cada pantalla, en un nuevo ojo. La mirada colectiva se multiplica a través de la red.',
];

const SPECS = [
  { label: 'CÁMARAS', value: '9' },
  { label: 'SERVOMOTORES', value: '18' },
  { label: 'PROCESAMIENTO', value: 'TIEMPO REAL' },
  { label: 'BASE DE DATOS', value: '_DB_COUNT_' },
  { label: 'PERÍODO', value: '2020–2026' },
  { label: 'REGIÓN', value: 'ESTADO DE MÉXICO' },
];

const PIPELINE_STEPS = [
  {
    num: '01',
    title: 'RECOLECCIÓN',
    desc: 'Los boletines de búsqueda son descargados diariamente del portal oficial de la Comisión de Búsqueda de Personas del Estado de México (COBUPEM). El sistema extrae automáticamente las imágenes y datos de cada caso publicado.',
  },
  {
    num: '02',
    title: 'PROCESAMIENTO FACIAL',
    desc: 'Un modelo de inteligencia artificial (InsightFace / buffalo_l) analiza cada boletín, detecta el rostro y genera un recorte facial normalizado. El modelo produce un embedding de 512 dimensiones — una huella matemática única del rostro.',
  },
  {
    num: '03',
    title: 'INDEXACIÓN',
    desc: 'Los embeddings faciales se almacenan en una base de datos vectorial. Cada entrada contiene el nombre, año, imagen recortada, boletín original y el vector de 512 dimensiones que representa la identidad facial.',
  },
  {
    num: '04',
    title: 'BÚSQUEDA POR SIMILITUD',
    desc: 'Cuando un visitante activa la cámara, el sistema captura su rostro, genera un embedding en tiempo real y lo compara contra toda la base de datos usando similitud coseno. Los 8 rostros más parecidos se muestran al instante.',
  },
  {
    num: '05',
    title: 'INFRAESTRUCTURA CLOUD',
    desc: 'El backend corre en HuggingFace Spaces como contenedor Docker con FastAPI + InsightFace. Las imágenes se sirven desde un CDN dedicado. El frontend está desplegado en Vercel como aplicación Next.js. Todo opera sin servidores propios.',
  },
  {
    num: '06',
    title: 'ACTUALIZACIÓN CONTINUA',
    desc: 'El sistema se actualiza periódicamente de forma automática: nuevos boletines son descargados, procesados e indexados. La base de datos crece con cada persona reportada como desaparecida, expandiendo el alcance de la búsqueda.',
  },
];

export default function HomePage() {
  const [visibleIdx, setVisibleIdx] = useState(-1);
  const [glitchLine, setGlitchLine] = useState(0);
  const [dbCount, setDbCount] = useState<string>('11,000+');
  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch database count
  useEffect(() => {
    fetch(`${API}/`)
      .then(r => r.json())
      .then(d => setDbCount((d.personas ?? 0).toLocaleString()))
      .catch(() => {});
  }, []);

  // Reveal paragraphs one by one
  useEffect(() => {
    const timers = PARAGRAPHS.map((_, i) =>
      setTimeout(() => setVisibleIdx(i), 600 + i * 900)
    );
    return () => timers.forEach(clearTimeout);
  }, []);

  // Glitch scan line
  useEffect(() => {
    const id = setInterval(() => {
      setGlitchLine(Math.random() * 100);
    }, 3000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className={styles.page} ref={containerRef}>
      {/* Scan line effect */}
      <div className={styles.scanLine} style={{ top: `${glitchLine}%` }} />

      {/* Navigation */}
      <nav className={styles.nav}>
        <span className={styles.navTag}>MIL OJOS</span>
        <span className={styles.navTag}>EXOESQUELETO DE VIGILANCIA AFECTIVA</span>
        <div style={{ display: 'flex', gap: 24 }}>
          <Link href="/escaneo" className={styles.navLink}>ESCANEO →</Link>
          <Link href="/explorar" className={styles.navLink}>EXPLORAR →</Link>
        </div>
      </nav>

      {/* ═══ SECCIÓN 1: Concepto ═══ */}
      <div className={styles.content}>
        {/* Left column — title + specs */}
        <div className={styles.left}>
          <div className={styles.titleBlock}>
            <span className={styles.tag}>pieza de arte electrónico</span>
            <h1 className={styles.title}>MIL<br />OJOS<span className={styles.cursor}>_</span></h1>
            <div className={styles.subtitle}>
              Exoesqueleto de vigilancia afectiva
            </div>
          </div>

          <div className={styles.specs}>
            {SPECS.map((s, i) => (
              <div key={i} className={styles.spec}>
                <span className={styles.specLabel}>{s.label}</span>
                <span className={styles.specValue}>{s.value === '_DB_COUNT_' ? `${dbCount} FICHAS` : s.value}</span>
              </div>
            ))}
          </div>

          <div className={styles.links}>
            <Link href="/escaneo" className={styles.ctaLink}>INICIAR ESCANEO →</Link>
            <Link href="/explorar" className={styles.extLink}>EXPLORAR BASE DE DATOS →</Link>
            <a
              href="https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas"
              target="_blank" rel="noopener noreferrer"
              className={styles.extLink}
            >
              COBUPEM — SITIO OFICIAL ↗
            </a>
          </div>
        </div>

        {/* Right column — text */}
        <div className={styles.right}>
          <div className={styles.textBlock}>
            {PARAGRAPHS.map((p, i) => (
              <p
                key={i}
                className={`${styles.paragraph} ${i <= visibleIdx ? styles.visible : ''}`}
                style={{ transitionDelay: `${i * 0.1}s` }}
              >
                {p}
              </p>
            ))}
          </div>

          <div className={styles.footnote}>
            <div className={styles.divider} />
            <p>
              El sistema opera de forma continua: nuevos boletines son descargados, procesados e indexados automáticamente. La base de datos crece con cada persona reportada, expandiendo el alcance de la búsqueda —en el exoesqueleto físico y en esta plataforma por igual.
            </p>
          </div>
        </div>
      </div>

      {/* ═══ SECCIÓN 2: Cómo funciona el sistema ═══ */}
      <div className={styles.systemSection}>
        <div className={styles.sectionHeader}>
          <span className={styles.tag}>arquitectura / pipeline</span>
          <h2 className={styles.sectionTitle}>CÓMO FUNCIONA EL SISTEMA<span className={styles.cursor}>_</span></h2>
          <p className={styles.sectionSub}>
            Cada día, un pipeline automatizado recorre el portal oficial de personas desaparecidas,
            extrae los boletines de búsqueda, procesa los rostros y actualiza la base de datos que
            alimenta tanto al exoesqueleto como a esta plataforma web.
          </p>
        </div>

        <div className={styles.pipeline}>
          {PIPELINE_STEPS.map((step) => (
            <div key={step.num} className={styles.pipelineStep}>
              <div className={styles.stepNum}>{step.num}</div>
              <div className={styles.stepContent}>
                <h3 className={styles.stepTitle}>{step.title}</h3>
                <p className={styles.stepDesc}>{step.desc}</p>
              </div>
              <div className={styles.stepLine} />
            </div>
          ))}
        </div>

        {/* Diagrama de flujo visual */}
        <div className={styles.flowDiagram}>
          <div className={styles.flowNode}>
            <span className={styles.flowIcon}>◉</span>
            <span className={styles.flowLabel}>COBUPEM</span>
          </div>
          <div className={styles.flowArrow}>→</div>
          <div className={styles.flowNode}>
            <span className={styles.flowIcon}>⬡</span>
            <span className={styles.flowLabel}>SCRAPER</span>
          </div>
          <div className={styles.flowArrow}>→</div>
          <div className={styles.flowNode}>
            <span className={styles.flowIcon}>◎</span>
            <span className={styles.flowLabel}>INSIGHTFACE</span>
          </div>
          <div className={styles.flowArrow}>→</div>
          <div className={styles.flowNode}>
            <span className={styles.flowIcon}>▣</span>
            <span className={styles.flowLabel}>DB VECTORIAL</span>
          </div>
          <div className={styles.flowArrow}>→</div>
          <div className={styles.flowNode} data-active="true">
            <span className={styles.flowIcon}>◈</span>
            <span className={styles.flowLabel}>MIL OJOS</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className={styles.footer}>
        <span className={styles.tag}>MIL OJOS — v2.0</span>
        <span className={styles.tag}>ACTUALIZACIÓN DIARIA AUTOMÁTICA</span>
        <span className={styles.tag}>EDOMEX 2020–2026</span>
      </div>
    </div>
  );
}
