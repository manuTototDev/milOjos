'use client';
import { use, useEffect, useState } from 'react';
import Link from 'next/link';
import styles from './page.module.css';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Ficha { id: number; name: string; year: string; foto: string; boletin: string; }

export default function FichaPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [ficha, setFicha] = useState<Ficha | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/fichas/${id}`)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(setFicha)
      .catch(() => setFicha(null))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div className={styles.loadingScreen}>
      <div className={styles.loadingPulse} />
      <span className={styles.loadingText}>CARGANDO FICHA…</span>
    </div>
  );

  if (!ficha) return (
    <div className={styles.loadingScreen}>
      <p className={styles.loadingText}>FICHA NO ENCONTRADA</p>
      <Link href="/explorar" className={styles.backLink}>← VOLVER</Link>
    </div>
  );

  const fotoSrc    = `${API}${ficha.foto}`;
  const boletinSrc = `${API}${ficha.boletin}`;

  return (
    <div className={styles.page}>
      {/* ── Nav superior ── */}
      <nav className={styles.topNav}>
        <Link href="/" className={styles.navLink}>← MIL OJOS</Link>
        <span className={styles.navTag}>FICHA #{String(ficha.id).padStart(5, '0')}</span>
        <Link href="/explorar" className={styles.navLink}>BASE DE DATOS →</Link>
      </nav>

      {/* ── Contenido principal: split layout ── */}
      <div className={styles.content}>
        {/* Lado izquierdo — foto recortada */}
        <div className={styles.fotoSide}>
          <img src={fotoSrc} alt={ficha.name} className={styles.foto} />
          <div className={styles.fotoOverlay}>
            <span className={styles.yearBadge}>{ficha.year}</span>
          </div>
        </div>

        {/* Lado derecho — boletín oficial */}
        <div className={styles.boletinSide}>
          <div className={styles.boletinHeader}>
            <span className={styles.tag}>boletín oficial / cobupem</span>
            <h1 className={styles.name}>{ficha.name}</h1>
            <p className={styles.sub}>Descripción física, señas particulares, vestimenta y número de reporte.</p>
          </div>
          <div className={styles.boletinScroll}>
            <img src={boletinSrc} alt={`Boletín de ${ficha.name}`} className={styles.boletin} />
          </div>
        </div>
      </div>

      {/* ── Footer nav ── */}
      <div className={styles.bottomNav}>
        {ficha.id > 0 ? (
          <Link href={`/ficha/${ficha.id - 1}`} className={styles.navBtn} id="btn-anterior-ficha">← ANTERIOR</Link>
        ) : <span />}
        <a href="https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas"
          target="_blank" rel="noopener noreferrer" className={styles.navBtn} id="btn-sitio-oficial-ficha">
          COBUPEM ↗
        </a>
        <Link href={`/ficha/${ficha.id + 1}`} className={styles.navBtn} id="btn-siguiente-ficha">SIGUIENTE →</Link>
      </div>
    </div>
  );
}
