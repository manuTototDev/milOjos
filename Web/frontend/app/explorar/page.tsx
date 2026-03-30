'use client';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import styles from './page.module.css';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const LIMIT = 48;

interface Ficha { id: number; name: string; year: string; foto: string; boletin: string; }
interface ApiResp { total: number; page: number; pages: number; items: Ficha[]; }

type SortField = 'none' | 'name' | 'year';
type SortDir   = 'asc' | 'desc';

export default function ExplorarPage() {
  const [fichas, setFichas]     = useState<Ficha[]>([]);
  const [total, setTotal]       = useState(0);
  const [pages, setPages]       = useState(1);
  const [page, setPage]         = useState(1);
  const [year, setYear]         = useState('');
  const [q, setQ]               = useState('');
  const [search, setSearch]     = useState('');
  const [years, setYears]       = useState<string[]>([]);
  const [loading, setLoading]   = useState(false);
  const [sortField, setSortField] = useState<SortField>('none');
  const [sortDir, setSortDir]     = useState<SortDir>('asc');

  useEffect(() => {
    fetch(`${API}/years`).then(r => r.json()).then(d => setYears(d.years));
  }, []);

  const fetchFichas = useCallback(async (pg: number, yr: string, qs: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(pg), limit: String(LIMIT) });
      if (yr) params.set('year', yr);
      if (qs) params.set('q', qs);
      const res = await fetch(`${API}/fichas?${params}`);
      const data: ApiResp = await res.json();
      setFichas(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchFichas(page, year, search); }, [page, year, search, fetchFichas]);

  // Client-side sort of current page items
  const sorted = [...fichas].sort((a, b) => {
    if (sortField === 'none') return 0;
    const dir = sortDir === 'asc' ? 1 : -1;
    if (sortField === 'name') return dir * a.name.localeCompare(b.name);
    if (sortField === 'year') {
      const yc = a.year.localeCompare(b.year);
      return yc !== 0 ? dir * yc : a.name.localeCompare(b.name);
    }
    return 0;
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    setSearch(q);
  };

  const handleYear = (yr: string) => { setYear(yr); setPage(1); };

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  };
  const clearSort = () => { setSortField('none'); setSortDir('asc'); };

  return (
    <div className={styles.page}>
      {/* ── Header ── */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.tag}>base de datos / explorar</span>
          <h1 className={styles.title}>FICHAS<span className={styles.cursor}>_</span></h1>
        </div>
        <div className={styles.headerRight}>
          <span className={styles.tag}>total</span>
          <span className={styles.count}>{total.toLocaleString()}</span>
          <span className={styles.tag}>personas registradas</span>
        </div>
      </div>

      {/* ── Filters bar ── */}
      <div className={styles.filtersBar}>
        <form onSubmit={handleSearch} className={styles.searchForm}>
          <input
            id="input-search"
            className={styles.searchInput}
            placeholder="Buscar por nombre…"
            value={q}
            onChange={e => setQ(e.target.value)}
          />
          <button type="submit" className={styles.searchBtn} id="btn-buscar">BUSCAR</button>
        </form>

        <div className={styles.filterGroup}>
          {/* Year pills */}
          <button
            className={`${styles.pill} ${!year ? styles.pillActive : ''}`}
            id="btn-year-all"
            onClick={() => handleYear('')}
          >
            TODOS
          </button>
          {years.map(yr => (
            <button
              key={yr}
              className={`${styles.pill} ${year === yr ? styles.pillActive : ''}`}
              id={`btn-year-${yr}`}
              onClick={() => handleYear(yr)}
            >
              {yr}
            </button>
          ))}
          
          {/* Sort buttons */}
          <div className={styles.sortDivider} />
          <span className={styles.sortLabel}>ORDENAR:</span>
          <button
            className={`${styles.sortBtn} ${sortField === 'name' ? styles.sortBtnActive : ''}`}
            onClick={() => toggleSort('name')}
            id="btn-sort-name"
          >
            NOMBRE {sortField === 'name' ? (sortDir === 'asc' ? '↑' : '↓') : ''}
          </button>
          <button
            className={`${styles.sortBtn} ${sortField === 'year' ? styles.sortBtnActive : ''}`}
            onClick={() => toggleSort('year')}
            id="btn-sort-year"
          >
            AÑO {sortField === 'year' ? (sortDir === 'asc' ? '↑' : '↓') : ''}
          </button>
          {sortField !== 'none' && (
            <button className={styles.sortBtn} onClick={clearSort} id="btn-sort-clear">✕</button>
          )}
        </div>
      </div>

      <div className={styles.divider} />

      {/* ── Grid ── */}
      <div className={styles.gridContainer}>
        {loading ? (
          <div className={styles.stateMsg}>
            <div className={styles.pulse} />
            <span>CARGANDO…</span>
          </div>
        ) : sorted.length === 0 ? (
          <div className={styles.stateMsg}>
            <span>SIN RESULTADOS</span>
          </div>
        ) : (
          <div className={styles.grid}>
            {sorted.map(f => (
              <Link key={f.id} href={`/ficha/${f.id}`} className={styles.card} id={`ficha-card-${f.id}`}>
                <img src={`${API}${f.foto}`} alt={f.name} className={styles.cardImg} loading="lazy" />
                <div className={styles.cardOverlay}>
                  <span className={styles.cardYear}>{f.year}</span>
                </div>
                <div className={styles.cardLabel}>
                  <span className={styles.cardName}>{f.name}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* ── Pagination ── */}
      {pages > 1 && !loading && (
        <div className={styles.pagination}>
          <button
            className={styles.pageBtn}
            id="btn-prev"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            ← ANTERIOR
          </button>

          <div className={styles.pageNumbers}>
            {Array.from({ length: Math.min(7, pages) }, (_, i) => {
              let pg = i + 1;
              if (pages > 7) {
                const start = Math.max(1, Math.min(page - 3, pages - 6));
                pg = start + i;
              }
              return (
                <button
                  key={pg}
                  className={`${styles.pageNum} ${pg === page ? styles.pageNumActive : ''}`}
                  id={`btn-page-${pg}`}
                  onClick={() => setPage(pg)}
                >
                  {pg}
                </button>
              );
            })}
          </div>

          <span className={styles.pageInfo}>{page} / {pages}</span>

          <button
            className={styles.pageBtn}
            id="btn-next"
            onClick={() => setPage(p => Math.min(pages, p + 1))}
            disabled={page === pages}
          >
            SIGUIENTE →
          </button>
        </div>
      )}
    </div>
  );
}
