import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pay OR Play — Ransomware Simulation Platform",
  description: "Defensive security research: attack lifecycle simulation and detection engine",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0a0e17] text-[#e0e6ed] font-mono overflow-hidden h-screen">
        {children}
      </body>
    </html>
  );
}
