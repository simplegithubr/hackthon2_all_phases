import type { Metadata } from "next";
import "../globals.css";

import { AuthProvider } from "../context/AuthContext";
import Navbar from "../components/Navbar";
import FloatingChat from "../components/FloatingChat";

export const metadata: Metadata = {
  title: "TaskFlow Pro - Task Management",
  description: "Modern task management app built with Next.js and FastAPI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <AuthProvider>
          {/* Navbar only shown on auth pages (login/signup) */}
          <div className="auth-navbar">
            <Navbar />
          </div>
          <main>{children}</main>
          <FloatingChat />
        </AuthProvider>
      </body>
    </html>
  );
}
