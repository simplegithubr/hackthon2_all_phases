"use client";

/**
 * Tasks page - displays all tasks for authenticated user
 * Client Component for auth protection
 */
import { useRequireAuth } from "../../context/AuthContext";
import TaskList from "./components/TaskList";

export default function TasksPage() {
  const { isLoading } = useRequireAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="relative">
            <div className="w-12 h-12 rounded-full border-4 border-gray-200"></div>
            <div className="absolute top-0 left-0 w-12 h-12 rounded-full border-4 border-violet-500 border-t-transparent animate-spin"></div>
          </div>
          <p className="mt-4 text-gray-500 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  return <TaskList />;
}
