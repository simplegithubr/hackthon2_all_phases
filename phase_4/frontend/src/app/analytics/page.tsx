"use client";

import { useRequireAuth } from "../../context/AuthContext";
import Sidebar from "../../components/layout/Sidebar";

export default function AnalyticsPage() {
  const { isLoading } = useRequireAuth();

  if (isLoading) {
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
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-3">Advanced Analytics</h1>
            <p className="text-lg text-gray-500">Powerful insights coming soon</p>
          </div>

          {/* Coming Soon Card */}
          <div className="glass-card p-12 text-center animate-fade-in">
            <div className="w-32 h-32 bg-gradient-to-br from-violet-100 to-fuchsia-100 rounded-full flex items-center justify-center mx-auto mb-8 animate-float">
              <svg className="w-16 h-16 text-violet-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 012 2v10m-6 0a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Analytics Coming Soon</h2>
            <p className="text-gray-500 mb-6 max-w-lg mx-auto">
              We're working on powerful analytics features to help you track your productivity trends,
              identify patterns, and optimize your workflow.
            </p>

            {/* Feature Preview Cards */}
            <div className="space-y-3 max-w-md mx-auto">
              <div className="flex items-center gap-4 p-5 rounded-xl bg-white/50 border border-white/20">
                <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 012 2v10m-6 0a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900">Productivity Charts</p>
                  <p className="text-sm text-gray-500">Visualize your task completion over time</p>
                </div>
              </div>

              <div className="flex items-center gap-4 p-5 rounded-xl bg-white/50 border border-white/20">
                <div className="w-12 h-12 rounded-xl bg-fuchsia-100 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-fuchsia-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-4l-4 4-4" />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900">Goal Tracking</p>
                  <p className="text-sm text-gray-500">Set and track daily/weekly goals</p>
                </div>
              </div>

              <div className="flex items-center gap-4 p-5 rounded-xl bg-white/50 border border-white/20">
                <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="font-medium text-gray-900">Trend Analysis</p>
                  <p className="text-sm text-gray-500">Identify patterns in your workflow</p>
                </div>
              </div>
            </div>

            {/* Pro Tip Card */}
            <div className="p-6 rounded-xl bg-gradient-to-r from-violet-50 to-fuchsia-50 border border-violet-100">
              <p className="text-sm text-gray-700 flex items-center gap-2">
                <span className="text-2xl">💡</span>
                <span className="font-medium">Pro Tip:</span>
              </p>
              <p className="text-sm text-gray-600 mt-2">
                In the meantime, check your{" "}
                <a href="/dashboard" className="text-violet-600 hover:text-violet-700 font-semibold">
                  Dashboard
                </a>
                {" "}
                for a quick overview of your tasks!
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
