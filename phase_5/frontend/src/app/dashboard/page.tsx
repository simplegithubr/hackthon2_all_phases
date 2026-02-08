"use client";

import { useEffect, useState } from "react";
import { useRequireAuth } from "../../context/AuthContext";
import { tasks } from "../../services/tasks";
import { Task } from "../../types/tasks";
import Sidebar from "../../components/layout/Sidebar";
import Link from "next/link";
import ChatBoard from "../../components/ChatBoard";

export default function DashboardPage() {
  const { isLoading: authLoading } = useRequireAuth();
  const [taskList, setTaskList] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadTasks() {
      try {
        const taskData = await tasks.fetchTasks();
        setTaskList(Array.isArray(taskData) ? taskData : []);
      } catch (err) {
        console.error("Failed to load tasks:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadTasks();
  }, []);

  const totalTasks = taskList.length;
  const completedTasks = taskList.filter((t) => t.is_complete).length;
  const pendingTasks = totalTasks - completedTasks;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex">
        <Sidebar />
        <main className="flex-1 ml-64 p-8 flex items-center justify-center">
          <div className="flex flex-col items-center">
            <div className="relative">
              <div className="w-16 h-16 rounded-full border-4 border-gray-200"></div>
              <div className="absolute top-0 left-0 w-16 h-16 rounded-full border-4 border-violet-500 border-t-transparent animate-spin"></div>
            </div>
            <p className="mt-4 text-gray-500 font-medium">Loading...</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex">
      <Sidebar />
      <main className="flex-1 ml-64 p-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-500 mt-1">Welcome back! Here's your productivity overview.</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Total Tasks */}
            <div className="glass-card p-6 animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <span className="text-xs text-gray-400">Total</span>
              </div>
              <h3 className="text-3xl font-bold text-gray-900">{totalTasks}</h3>
              <p className="text-sm text-gray-500 mt-1">Total Tasks</p>
            </div>

            {/* Completed */}
            <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: "0.1s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-xs text-gray-400">Done</span>
              </div>
              <h3 className="text-3xl font-bold text-emerald-600">{completedTasks}</h3>
              <p className="text-sm text-gray-500 mt-1">Completed</p>
            </div>

            {/* Pending */}
            <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: "0.2s" }}>
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-xs text-gray-400">Active</span>
              </div>
              <h3 className="text-3xl font-bold text-amber-600">{pendingTasks}</h3>
              <p className="text-sm text-gray-500 mt-1">Pending</p>
            </div>
          </div>

          {/* Progress Card */}
          <div className="glass-card p-6 mb-8 animate-fade-in" style={{ animationDelay: "0.3s" }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Completion Rate</h3>
              <span className="text-2xl font-bold text-violet-600">{completionRate}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full transition-all duration-1000 ease-out"
                style={{ width: `${completionRate}%` }}
              />
            </div>
            <p className="text-sm text-gray-500 mt-3">
              {completionRate === 100
                ? "Amazing! You've completed all your tasks! 🎉"
                : completionRate >= 75
                ? "Great progress! Keep it up! 💪"
                : completionRate >= 50
                ? "Halfway there! You're doing great! 🚀"
                : "Let's get started! Create some tasks! ✨"}
            </p>
          </div>

          {/* Recent Tasks */}
          <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: "0.4s" }}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Recent Tasks</h3>
              <Link
                href="/tasks"
                className="text-sm text-violet-600 hover:text-violet-700 font-medium"
              >
                View All →
              </Link>
            </div>

            {taskList.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <p className="text-gray-500 mb-4">No tasks yet</p>
                <Link
                  href="/tasks"
                  className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white font-medium rounded-xl hover:from-violet-600 hover:to-fuchsia-600 transition-all"
                >
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Create Task
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {taskList.slice(0, 5).map((task) => (
                  <div
                    key={task.id}
                    className={`p-4 rounded-xl border transition-all duration-200 ${
                      task.is_complete
                        ? "bg-emerald-50/50 border-emerald-200"
                        : "bg-white/50 border-gray-200"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-6 h-6 rounded-lg flex items-center justify-center ${
                          task.is_complete
                            ? "bg-emerald-500"
                            : "border-2 border-gray-300 bg-white"
                        }`}
                      >
                        {task.is_complete && (
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4
                          className={`font-medium truncate ${
                            task.is_complete ? "text-gray-400 line-through" : "text-gray-900"
                          }`}
                        >
                          {task.title}
                        </h4>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Chat Board Section */}
          <div className="mt-8">
            <ChatBoard />
          </div>
        </div>
      </main>
    </div>
  );
}
