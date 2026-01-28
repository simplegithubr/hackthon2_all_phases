/**
 * Landing page
 */
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-50 via-fuchsia-50 to-pink-50 px-4">
      <div className="max-w-md mx-auto w-full">
        <div className="glass-card p-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Welcome to Todo App
          </h1>

          <p className="text-gray-600 mb-8">
            Simple task management to help you stay organized
          </p>

          <Link
            href="/tasks"
            className="w-full inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-violet-500 via-fuchsia-500 to-pink-500 text-white font-semibold rounded-xl hover:from-violet-600 hover:via-fuchsia-600 hover:to-pink-600 transition-all shadow-lg shadow-fuchsia-500/30 hover:shadow-fuchsia-500/50 hover:scale-105 mb-4"
          >
            Get Started
          </Link>

          <Link
            href="/login"
            className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
