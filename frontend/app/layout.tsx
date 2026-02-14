import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CV RAG Dashboard",
  description: "Manage jobs, uploads, rankings and chat",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
