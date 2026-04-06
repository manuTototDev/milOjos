// deploy: 2026-04-06
import type { Metadata } from "next";
import "./globals.css";
import LoadingGate from "@/components/LoadingGate";

export const metadata: Metadata = {
  title: "MIL OJOS — Sistema de reconocimiento facial",
  description: "Sistema de búsqueda por similitud facial. Base de datos de personas desaparecidas en el Estado de México. COBUPEM 2020–2026.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <LoadingGate>{children}</LoadingGate>
      </body>
    </html>
  );
}
