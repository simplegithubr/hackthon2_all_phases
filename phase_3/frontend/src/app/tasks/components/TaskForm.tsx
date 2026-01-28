"use client";

/**
 * TaskForm component - create or edit tasks
 * Client Component for interactivity
 */
import { useState, FormEvent } from "react";
import { Task, TaskCreate, TaskUpdate, validateTaskTitle, PriorityLevel } from "../../../types/tasks";
import { tasks } from "../../../services/tasks";

interface TaskFormProps {
  mode?: "create" | "edit";
  initialData?: Partial<Task>;
  taskId?: number;
  onSuccess?: () => void;
}

export default function TaskForm({
  mode = "create",
  initialData,
  taskId,
  onSuccess,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [priority, setPriority] = useState<"high" | "medium" | "low">(initialData?.priority || "medium");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    // Validate title
    const validationResult = validateTaskTitle(title);
    if (validationResult !== true) {
      setError(validationResult);
      return;
    }

    setIsSubmitting(true);

    try {
      if (mode === "create") {
        // Create new task
        const taskData: TaskCreate = { title, priority };
        if (description && description.trim()) {
          taskData.description = description;
        }
        await tasks.createTask(taskData);
      } else if (mode === "edit" && taskId) {
        // Update existing task
        const taskData: TaskUpdate = { title, priority };
        if (description !== undefined) {
          taskData.description = description;
        }
        await tasks.updateTask(taskId, taskData);
      }

      // Clear form on success
      setTitle("");
      setDescription("");
      setPriority("medium");

      // Notify parent to refresh task list
      if (onSuccess) {
        onSuccess();
      } else {
        // Reload page to refresh task list
        window.location.reload();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save task");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-300 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        {mode === "create" ? "Create New Task" : "Edit Task"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title Field */}
        <div>
          <label
            htmlFor="title"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Task Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Buy groceries"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
            maxLength={200}
          />
          <p className="mt-1 text-sm text-gray-500">
            {title.length}/200 characters
          </p>
        </div>

        {/* Description Field */}
        <div>
          <label
            htmlFor="description"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Description <span className="text-gray-400">(optional)</span>
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add details about this task..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Priority Field */}
        <div>
          <label
            htmlFor="priority"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as "high" | "medium" | "low")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="high">🔴 High Priority</option>
            <option value="medium">🟠 Medium Priority</option>
            <option value="low">🟢 Low Priority</option>
          </select>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className={`w-full px-4 py-2 rounded-md font-medium text-white transition-colors ${
            isSubmitting
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {isSubmitting ? "Saving..." : mode === "create" ? "Create Task" : "Update Task"}
        </button>
      </form>
    </div>
  );
}
