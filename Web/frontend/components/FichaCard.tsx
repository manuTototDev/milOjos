import Link from 'next/link';
import styles from './FichaCard.module.css';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Props {
  id: number;
  name: string;
  year: string;
  foto: string;
  boletin?: string;
  score?: number;
  rank?: number;
}

export default function FichaCard({ id, name, year, foto, score, rank }: Props) {
  const imgSrc = `${API}${foto}`;
  const scoreColor = score !== undefined
    ? score > 60 ? '#4ade80' : score > 40 ? '#f4a261' : '#8896a8'
    : undefined;

  return (
    <Link href={`/ficha/${id}`} className={styles.card} id={`ficha-card-${id}`}>
      {rank !== undefined && (
        <div className={styles.rank}>#{rank}</div>
      )}
      <div className={styles.imgWrapper}>
        <img src={imgSrc} alt={name} className={styles.img} loading="lazy" />
      </div>
      <div className={styles.info}>
        <p className={styles.name}>{name}</p>
        <div className={styles.meta}>
          <span className="badge badge-gray">{year}</span>
          {score !== undefined && (
            <span className={styles.score} style={{ color: scoreColor }}>
              {score.toFixed(1)}%
            </span>
          )}
        </div>
        {score !== undefined && (
          <div className="score-bar-bg" style={{ marginTop: 8 }}>
            <div className="score-bar-fill" style={{ width: `${Math.min(score, 100)}%` }} />
          </div>
        )}
      </div>
    </Link>
  );
}
