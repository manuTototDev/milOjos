import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "EXPLORAR — MIL OJOS",
  description: "Explorar base de datos de personas desaparecidas. Estado de México 2020–2026.",
};

export default function ExplorarLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ minHeight: '100vh', background: '#000', display: 'flex', flexDirection: 'column' }}>
      <nav style={{
        height: 44, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 24px', borderBottom: '1px solid rgba(255,255,255,0.07)', flexShrink: 0
      }}>
        <Link href="/" style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.2em', color: 'rgba(255,255,255,0.4)', textDecoration: 'none' }}>
          ← MIL OJOS
        </Link>
        <span style={{ fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.18em', color: 'rgba(255,255,255,0.2)' }}>
          BASE DE DATOS / FICHAS
        </span>
        <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
          <Link href="/escaneo" style={{ fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.15em', color: 'rgba(255,255,255,0.25)', textDecoration: 'none' }}>
            ESCANEO
          </Link>
          <a href="https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas"
            target="_blank" rel="noopener noreferrer"
            style={{ fontFamily: 'var(--mono)', fontSize: 9, letterSpacing: '0.15em', color: 'rgba(255,255,255,0.25)', textDecoration: 'none' }}>
            COBUPEM ↗
          </a>
        </div>
      </nav>
      <div style={{ flex: 1, overflow: 'auto' }}>{children}</div>
    </div>
  );
}
