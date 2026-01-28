"use client";

/**
 * Navbar component - auth-aware navigation with logout
 */
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../context/AuthContext";
import { Button } from "./ui";

export default function Navbar() {
  const router = useRouter();
  const { isAuthenticated, user, logout, isLoading } = useAuth();

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-blue-600">
            Todo App
          </Link>

          <div className="flex items-center gap-4">
            {isLoading ? (
              // Loading state
              <div className="animate-pulse bg-gray-200 h-8 w-20 rounded" />
            ) : isAuthenticated ? (
              // Authenticated state
              <>
                <span className="text-sm text-gray-600 hidden sm:block">
                  {user?.email}
                </span>
                <Link href="/tasks">
                  <Button variant="secondary" size="sm">
                    My Tasks
                  </Button>
                </Link>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </>
            ) : (
              // Unauthenticated state
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    Sign In
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button size="sm">Sign Up</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
