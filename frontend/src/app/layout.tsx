import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Code Intelligence Studio | Autonomous Engineering Platform",
  description: "Autonomous AI Software Engineering & Repository Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-root text-slate-100 min-h-screen antialiased flex flex-col">
        {children}
      </body>
    </html>
  );
}
