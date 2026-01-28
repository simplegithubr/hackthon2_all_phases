"use client";

/**
 * TaskList component - displays list of tasks with TaskForm
 * Client Component for interactivity (loading, error states)
 */
import { useEffect, useState } from "react";
import { tasks } from "../../../services/tasks";
import { Task, formatTaskDate, getPriorityBadgeStyles } from "../../../types/tasks";
import TaskForm from "./TaskForm";
import DeleteConfirm from "./DeleteConfirm";
import Sidebar from "../../../components/layout/Sidebar";
import TopBar from "../../../components/layout/TopBar";
import QuickActions from "../../../components/layout/QuickActions";
import FloatingActionButton from "../../../components/layout/FloatingActionButton";

export default function TaskList() {
  const [taskList, setTaskList] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [priorityFilter, setPriorityFilter] = useState("all");

  // Calculate stats
  const completedTasks = taskList.filter((t) => t.is_complete);
  const pendingTasks = taskList.filter((t) => !t.is_complete);
  const highPriorityTasks = taskList.filter((t) => t.priority === "high" && !t.is_complete);

  // Calculate "Done Today" - tasks completed today
  const getCompletedToday = (): number => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return completedTasks.filter((task) => {
      const taskDate = new Date(task.updated_at);
      return task.is_complete && taskDate >= today;
    }).length;
  };

  const completedToday = getCompletedToday();
  const highPriorityCount = highPriorityTasks.length;

  // Filter and sort tasks
  useEffect(() => {
    let filtered = [...taskList];

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      filtered = filtered.filter(
        (task) =>
          task.title.toLowerCase().includes(query) ||
          (task.description && task.description.toLowerCase().includes(query))
      );
    }

    // Status filter
    if (activeFilter === "active") {
      filtered = filtered.filter((task) => !task.is_complete);
    } else if (activeFilter === "completed") {
      filtered = filtered.filter((task) => task.is_complete);
    }

    // Priority filter
    if (priorityFilter !== "all") {
      filtered = filtered.filter((task) => task.priority === priorityFilter);
    }

    // Sort
    if (sortBy === "newest") {
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    } else if (sortBy === "oldest") {
      filtered.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    } else if (sortBy === "title") {
      filtered.sort((a, b) => a.title.localeCompare(b.title));
    }

    setFilteredTasks(filtered);
  }, [taskList, searchQuery, activeFilter, sortBy, priorityFilter]);

  useEffect(() => {
    async function loadTasks() {
      try {
        setIsLoading(true);
        setError(null);
        const taskData = await tasks.fetchTasks();
        setTaskList(Array.isArray(taskData) ? taskData : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load tasks");
      } finally {
        setIsLoading(false);
      }
    }

    loadTasks();
  }, []);

  // Function to reload task list after creating/updating a task
  async function reloadTasks() {
    try {
      setIsLoading(true);
      setError(null);
      const taskData = await tasks.fetchTasks();
      setTaskList(Array.isArray(taskData) ? taskData : []);
      setShowForm(false);
      setEditingTask(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  }

  // Function to toggle task completion
  async function toggleTaskCompletion(taskId: number) {
    try {
      setError(null);
      const updatedTask = await tasks.toggleComplete(taskId);

      // Reload the full task list to ensure consistency
      await reloadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to toggle task completion");
      setTimeout(() => setError(null), 3000);
    }
  }

  // Function to open edit modal
  function openEditModal(task: Task) {
    setEditingTask(task);
    setShowForm(true);
  }

  // Function to open delete confirmation modal
  function openDeleteModal(task: Task) {
    setTaskToDelete(task);
    setShowDeleteConfirm(true);
  }

  // Function to handle task deletion
  async function handleDeleteTask() {
    if (!taskToDelete) return;

    try {
      await tasks.deleteTask(taskToDelete.id);
      setShowDeleteConfirm(false);
      setTaskToDelete(null);
      await reloadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete task");
    }
  }

  // Loading state
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
            <p className="mt-4 text-gray-500 font-medium animate-pulse">Loading your tasks...</p>
          </div>
        </main>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex">
        <Sidebar />
        <main className="flex-1 ml-64 p-8">
          <div className="max-w-2xl mx-auto mt-20">
            <div className="glass-card p-8 text-center">
              <div className="w-16 h-16 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Something went wrong</h3>
              <p className="text-gray-500 mb-6">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-3 bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white font-medium rounded-xl hover:from-violet-600 hover:to-fuchsia-600 transition-all shadow-lg"
              >
                Try Again
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  // Empty state
  if (!taskList || taskList.length === 0) {
    return (
      <div className="min-h-screen flex">
        <Sidebar />
        <main className="flex-1 ml-64 p-8">
          <div className="max-w-2xl mx-auto mt-20">
            {/* Empty State Card */}
            <div className="glass-card p-12 text-center animate-fade-in">
              <div className="w-24 h-24 bg-gradient-to-br from-violet-100 to-fuchsia-100 rounded-full flex items-center justify-center mx-auto mb-6 animate-float">
                <svg className="w-12 h-12 text-violet-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">No tasks yet</h2>
              <p className="text-gray-500 mb-8 max-w-sm mx-auto">
                Create your first task to start tracking your work and boost your productivity.
              </p>
              <button
                onClick={() => setShowForm(true)}
                className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white font-semibold rounded-xl hover:from-violet-600 hover:to-fuchsia-600 transition-all shadow-lg shadow-violet-500/30 hover:shadow-violet-500/50 hover:scale-105"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Your First Task
              </button>
            </div>
          </div>

          {/* Task Form Modal */}
          {showForm && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <div
                className="absolute inset-0 bg-gray-900/40 backdrop-blur-sm"
                onClick={() => {
                  setShowForm(false);
                  setEditingTask(null);
                }}
              />
              <div className="relative glass-card max-w-md w-full p-6 animate-modal-in">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-900">
                    {editingTask ? "Edit Task" : "Create New Task"}
                  </h3>
                  <button
                    onClick={() => {
                      setShowForm(false);
                      setEditingTask(null);
                    }}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/50 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <TaskForm
                  mode={editingTask ? "edit" : "create"}
                  initialData={editingTask || undefined}
                  taskId={editingTask?.id}
                  onSuccess={reloadTasks}
                />
              </div>
            </div>
          )}

          <FloatingActionButton onClick={() => setShowForm(true)} />
        </main>
      </div>
    );
  }

  // Task list
  return (
    <div className="min-h-screen flex">
      <Sidebar />

      <main className="flex-1 ml-64 p-8">
        <div className="max-w-5xl mx-auto">
          <TopBar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            activeFilter={activeFilter}
            onFilterChange={setActiveFilter}
            totalTasks={taskList.length}
            sortBy={sortBy}
            onSortChange={setSortBy}
            priority={priorityFilter}
            onPriorityChange={setPriorityFilter}
          />

          <div className="flex gap-6">
            {/* Main Content - Task List */}
            <div className="flex-1">
              {/* Error Toast */}
              {error && (
                <div className="mb-6 glass-card p-4 flex items-center bg-rose-50/80 border-rose-200">
                  <svg className="w-5 h-5 text-rose-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-rose-700">{error}</p>
                </div>
              )}

              {/* Task Items */}
              <div className="space-y-3">
                {filteredTasks.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onEdit={openEditModal}
                    onDelete={openDeleteModal}
                    onToggleComplete={toggleTaskCompletion}
                  />
                ))}
              </div>

              {filteredTasks.length === 0 && (
                <div className="glass-card p-12 text-center">
                  <p className="text-gray-500">No tasks match your filters.</p>
                </div>
              )}
            </div>

            {/* Right Sidebar - Quick Actions */}
            <div className="w-72 flex-shrink-0">
              <QuickActions
                onAddTask={() => setShowForm(true)}
                highPriorityCount={highPriorityCount}
                completedToday={completedToday}
                totalTasks={taskList.length}
              />
            </div>
          </div>
        </div>

        {/* Task Form Modal */}
        {showForm && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
              className="absolute inset-0 bg-gray-900/40 backdrop-blur-sm"
              onClick={() => {
                setShowForm(false);
                setEditingTask(null);
              }}
            />
            <div className="relative glass-card max-w-md w-full p-6 animate-modal-in">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900">
                  {editingTask ? "Edit Task" : "Create New Task"}
                </h3>
                <button
                  onClick={() => {
                    setShowForm(false);
                    setEditingTask(null);
                  }}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-white/50 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <TaskForm
                mode={editingTask ? "edit" : "create"}
                initialData={editingTask || undefined}
                taskId={editingTask?.id}
                onSuccess={reloadTasks}
              />
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && taskToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
              className="absolute inset-0 bg-gray-900/40 backdrop-blur-sm"
              onClick={() => {
                setShowDeleteConfirm(false);
                setTaskToDelete(null);
              }}
            />
            <div className="relative glass-card max-w-sm w-full p-6 animate-modal-in">
              <div className="text-center">
                <div className="w-14 h-14 bg-rose-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-7 h-7 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Delete Task</h3>
                <p className="text-gray-500 mb-6">
                  Are you sure you want to delete <span className="font-medium text-gray-700">"{taskToDelete.title}"</span>?
                </p>
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setTaskToDelete(null);
                    }}
                    className="flex-1 px-4 py-2.5 glass-button text-gray-700 font-medium rounded-xl"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDeleteTask}
                    className="flex-1 px-4 py-2.5 bg-gradient-to-r from-rose-500 to-pink-600 text-white font-medium rounded-xl hover:from-rose-600 hover:to-pink-700 transition-all"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <FloatingActionButton onClick={() => setShowForm(true)} />
      </main>
    </div>
  );
}

/**
 * TaskItem component - displays a single task with glassmorphism design
 */
interface TaskItemProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (task: Task) => void;
  onToggleComplete?: (taskId: number) => void;
}

function TaskItem({ task, onEdit, onDelete, onToggleComplete }: TaskItemProps) {
  const isComplete = task.is_complete;
  const priorityStyles = getPriorityBadgeStyles(task.priority);

  return (
    <div
      className={`group glass-card p-4 transition-all duration-300 hover:shadow-glass-hover hover:bg-white/70 ${
        isComplete ? "opacity-60" : ""
      }`}
    >
      <div className="flex items-start gap-4">
        {/* Custom Checkbox */}
        <button
          onClick={() => onToggleComplete && onToggleComplete(task.id)}
          className={`flex-shrink-0 w-6 h-6 rounded-lg border-2 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-violet-400/50 focus:ring-offset-2 ${
            isComplete
              ? "bg-gradient-to-r from-violet-500 to-fuchsia-500 border-transparent shadow-lg shadow-violet-500/30"
              : "border-gray-300 hover:border-violet-500 bg-white/50"
          }`}
        >
          {isComplete && (
            <svg className="w-full h-full p-0.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-base font-semibold transition-all duration-200 ${
              isComplete
                ? "text-gray-400 line-through"
                : "text-gray-800"
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`mt-1.5 text-sm line-clamp-2 ${
                isComplete ? "text-gray-400" : "text-gray-500"
              }`}
            >
              {task.description}
            </p>
          )}
          <div className="flex items-center gap-3 mt-3">
            <span className="text-xs px-2 py-0.5 rounded-full font-medium flex items-center gap-1.5">
              {priorityStyles.icon}
              <span className={priorityStyles.text}>{priorityStyles.label}</span>
            </span>
            <span className="text-xs text-gray-400 flex items-center gap-1">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {formatTaskDate(task.created_at)}
            </span>
            {!isComplete && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 font-medium">
                Active
              </span>
            )}
          </div>
        </div>

        {/* Action Buttons - Visible on hover */}
        <div className="opacity-0 group-hover:opacity-100 transition-all duration-200 flex items-center gap-1 ml-2">
          <button
            className="p-2.5 text-gray-500 hover:text-violet-600 hover:bg-violet-50 rounded-lg transition-colors"
            onClick={() => onEdit && onEdit(task)}
            title="Edit"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            className="p-2.5 text-gray-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
            onClick={() => onDelete && onDelete(task)}
            title="Delete"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
