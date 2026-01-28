"use client";

interface FloatingActionButtonProps {
  onClick: () => void;
}

export default function FloatingActionButton({ onClick }: FloatingActionButtonProps) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-8 right-8 z-50 w-14 h-14 rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-lg shadow-violet-500/40 hover:shadow-violet-500/60 hover:from-violet-600 hover:to-fuchsia-600 transition-all duration-300 hover:scale-110 active:scale-95 flex items-center justify-center group"
      aria-label="Add new task"
    >
      <svg
        className="w-6 h-6 transition-transform duration-300 group-hover:rotate-90"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
      </svg>

      {/* Pulse effect ring */}
      <span className="absolute inset-0 rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500 animate-ping opacity-25" />
    </button>
  );
}
