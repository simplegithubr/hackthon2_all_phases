// TypeScript type definitions for Task CRUD feature
// Auto-generated from SQLModel backend models

/**
 * Task entity representing a todo item
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  is_complete: boolean;
  priority: "high" | "medium" | "low";
  created_at: string;  // ISO 8601 datetime string
  updated_at: string;  // ISO 8601 datetime string
}

/**
 * Request body for creating a new task
 */
export interface TaskCreate {
  title: string;       // Required, max 200 characters
  description?: string;  // Optional
  priority?: "high" | "medium" | "low";  // Optional, defaults to "medium"
}

/**
 * Request body for updating an existing task
 * All fields are optional - only provided fields will be updated
 */
export interface TaskUpdate {
  title?: string;       // Optional, max 200 characters if provided
  description?: string;  // Optional
  priority?: "high" | "medium" | "low";  // Optional
}

/**
 * Response containing list of tasks
 */
export interface TaskList {
  tasks: Task[];
}

/**
 * Standard error response from API
 */
export interface APIError {
  detail: string;
}

/**
 * HTTP status codes for task API responses
 */
export const TaskAPIStatus = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const;

/**
 * Error detail messages from API
 */
export const TaskAPIErrors = {
  MISSING_TITLE: "Task title is required",
  TITLE_TOO_LONG: "Task title cannot exceed 200 characters",
  AUTH_REQUIRED: "Authentication required",
  INVALID_TOKEN: "Invalid or expired token",
  PERMISSION_DENIED: "You don't have permission to access this task",
  TASK_NOT_FOUND: "Task not found",
  SERVER_ERROR: "Something went wrong. Please try again.",
} as const;

/**
 * Validation rules for tasks (frontend)
 */
export const TaskValidation = {
  MAX_TITLE_LENGTH: 200,
} as const;

/**
 * Helper function to validate task title
 * @returns true if valid, error message if invalid
 */
export function validateTaskTitle(title: string): true | string {
  if (!title || title.trim().length === 0) {
    return TaskAPIErrors.MISSING_TITLE;
  }
  if (title.length > TaskValidation.MAX_TITLE_LENGTH) {
    return TaskAPIErrors.TITLE_TOO_LONG;
  }
  return true;
}

/**
 * Helper function to format ISO date string to readable date
 * @param isoDate - ISO 8601 datetime string
 * @returns Formatted date string (e.g., "Dec 31, 2025 at 10:00 AM")
 */
export function formatTaskDate(isoDate: string): string {
  const date = new Date(isoDate);
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
  }).format(date);
}

/**
 * Task completion status enum for UI
 */
export enum TaskCompletionStatus {
  INCOMPLETE = "incomplete",
  COMPLETE = "complete",
}

/**
 * Get task completion status from is_complete boolean
 */
export function getTaskCompletionStatus(task: Task): TaskCompletionStatus {
  return task.is_complete ? TaskCompletionStatus.COMPLETE : TaskCompletionStatus.INCOMPLETE;
}

/**
 * Priority levels enum for UI
 */
export enum PriorityLevel {
  HIGH = "high",
  MEDIUM = "medium",
  LOW = "low",
}

/**
 * Get priority badge color classes
 */
export function getPriorityBadgeStyles(priority: "high" | "medium" | "low"): {
  bg: string;
  text: string;
  icon: string;
  label: string;
} {
  switch (priority) {
    case "high":
      return {
        bg: "bg-rose-100",
        text: "text-rose-700",
        icon: "🔴",
        label: "High",
      };
    case "medium":
      return {
        bg: "bg-amber-100",
        text: "text-amber-700",
        icon: "🟠",
        label: "Medium",
      };
    case "low":
      return {
        bg: "bg-emerald-100",
        text: "text-emerald-700",
        icon: "🟢",
        label: "Low",
      };
    default:
      return {
        bg: "bg-gray-100",
        text: "text-gray-700",
        icon: "⚪",
        label: "Medium",
      };
  }
}
