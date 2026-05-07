import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Mil Ojos — Sistema de Vigilancia IA',
  description: 'Sistema de reconocimiento facial en tiempo real',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
