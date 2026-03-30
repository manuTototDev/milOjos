import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MIL OJOS — Sistema de reconocimiento facial",
  description: "Sistema de búsqueda por similitud facial. Base de datos de personas desaparecidas en el Estado de México. COBUPEM 2020–2026.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
