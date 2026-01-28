"use client";

interface QuickActionsProps {
  onAddTask: () => void;
  highPriorityCount?: number;
  completedToday?: number;
  totalTasks?: number;
}

export default function QuickActions({
  onAddTask,
  highPriorityCount = 0,
  completedToday = 0,
  totalTasks = 0,
}: QuickActionsProps) {
  return (
    <div className="glass-card p-5 space-y-4">
      <h3 className="font-semibold text-gray-800 flex items-center gap-2">
        <svg className="w-5 h-5 text-violet-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Quick Actions
      </h3>

      {/* Add Task Button */}
      <button
        onClick={onAddTask}
        className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white font-medium rounded-xl hover:from-violet-600 hover:to-fuchsia-600 transition-all shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Add New Task
      </button>

      {/* Stats */}
      <div className="space-y-3 pt-2 border-t border-white/20">
        <div className="flex items-center justify-between p-3 rounded-lg bg-rose-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-rose-100 flex items-center justify-center">
              <svg className="w-4 h-4 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <span className="text-sm text-gray-600">High Priority</span>
          </div>
          <span className="font-bold text-rose-600">{highPriorityCount}</span>
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-emerald-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
              <svg className="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="text-sm text-gray-600">Done Today</span>
          </div>
          <span className="font-bold text-emerald-600">{completedToday}</span>
        </div>

        <div className="flex items-center justify-between p-3 rounded-lg bg-blue-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span className="text-sm text-gray-600">Total Tasks</span>
          </div>
          <span className="font-bold text-blue-600">{totalTasks}</span>
        </div>
      </div>

      {/* Productivity Tip */}
      <div className="p-4 rounded-xl bg-gradient-to-br from-violet-50 to-fuchsia-50 border border-violet-100">
        <p className="text-xs text-gray-600 mb-2 font-medium">💡 Productivity Tip</p>
        <p className="text-xs text-gray-500">
          Complete your hardest task first thing in the morning for maximum productivity!
        </p>
      </div>
    </div>
  );
}
