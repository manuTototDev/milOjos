'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Navbar.module.css';

export default function Navbar() {
  const path = usePathname();
  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        <Link href="/" className="navbar-logo">
          <div className="navbar-eye">👁</div>
          MIL<span>OJOS</span>
        </Link>
        <ul className="navbar-links">
          <li><Link href="/" className={path === '/' ? 'active' : ''}>Búsqueda Facial</Link></li>
          <li><Link href="/explorar" className={path?.startsWith('/explorar') ? 'active' : ''}>Explorar Fichas</Link></li>
          <li>
            <a href="https://cobupem.edomex.gob.mx/boletines-personas-desaparecidas" target="_blank" rel="noopener noreferrer">
              Sitio Oficial ↗
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
}
