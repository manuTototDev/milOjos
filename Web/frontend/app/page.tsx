'use client';
import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import styles from './home.module.css';

const PARAGRAPHS = [
  'Mil Ojos es una pieza de arte electrónico en forma de exoesqueleto equipado con nueve cámaras móviles distribuidas alrededor de la cabeza del portador. Cada cámara está montada sobre servomotores que le permiten moverse de forma independiente, girar y seguir objetos visuales. El sistema cuenta con un módulo de inteligencia artificial que compara en tiempo real los rostros detectados en el entorno con una base de datos de personas desaparecidas en México.',
  'Esta obra parte de una imposibilidad humana: reconocer, retener y cotejar los cientos de rostros de personas desaparecidas que circulan diariamente en afiches, pantallas o redes sociales. La pieza actúa como una metáfora técnica de una memoria extendida, un cuerpo expandido que busca incansablemente entre la multitud. Cada cámara, cada servo, cada conexión de datos, se convierte en un ojo vigilante que no olvida, que insiste.',
  'El proyecto propone una reflexión sobre el duelo colectivo, la vigilancia afectiva y la carga que implica la memoria social. La obra opera como un gesto poético y político que explora cómo el cuerpo puede ser habitado por la tecnología no como arma, sino como órgano de búsqueda.',
  'Esta página funciona como extensión digital del proyecto: permite a cualquier persona, desde cualquier lugar, interactuar remotamente con el sistema de reconocimiento facial de Mil Ojos. A través de la cámara de su propio dispositivo, el visitante puede explorar la base de datos y experimentar la misma lógica de búsqueda que opera el exoesqueleto en el espacio físico. La web abre la pieza al territorio de lo remoto, extendiendo sus ojos más allá del cuerpo del portador, multiplicando la mirada colectiva a través de la red.',
];

const SPECS = [
  { label: 'CÁMARAS', value: '9' },
  { label: 'SERVOMOTORES', value: '18' },
  { label: 'PROCESAMIENTO', value: 'TIEMPO REAL' },
  { label: 'BASE DE DATOS', value: '11,375 FICHAS' },
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
    title: 'ACTUALIZACIÓN CONTINUA',
    desc: 'El sistema se actualiza diariamente de forma automática: nuevos boletines son descargados, procesados e indexados. La base de datos crece con cada persona reportada como desaparecida, expandiendo el alcance de la búsqueda.',
  },
];

export default function HomePage() {
  const [visibleIdx, setVisibleIdx] = useState(-1);
  const [glitchLine, setGlitchLine] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

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
                <span className={styles.specValue}>{s.value}</span>
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
              La pieza opera como un elemento paralelo —un cuerpo protésico que extiende las capacidades
              de reconocimiento humano hacia los márgenes de la memoria colectiva. Esta plataforma web
              traslada esa prótesis al espacio digital: cada visitante se convierte en portador remoto,
              cada pantalla en un nuevo ojo.
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
