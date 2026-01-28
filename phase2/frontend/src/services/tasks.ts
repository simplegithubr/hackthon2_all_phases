/**
 * Task API service for communicating with backend
 * Provides type-safe methods for all task CRUD operations
 */
import {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskList,
  APIError,
  TaskAPIErrors,
} from "../types/tasks";

/**
 * TaskService class for managing task API calls
 */
export class TaskService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "https://sagardeveloper-todo-phase2.hf.space";
  }

  /**
   * Get JWT token from cookies
   * @returns JWT token or null if not found
   */
  private getToken(): string | null {
    // In a real app, this would read from HTTP-only cookies
    // For now, we'll look for it in localStorage for development
    if (typeof window === "undefined") return null;
    return localStorage.getItem("jwt_token");
  }

  /**
   * Set JWT token in storage
   * @param token - JWT token from authentication
   */
  public setToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("jwt_token", token);
  }

  /**
   * Clear JWT token from storage
   */
  public clearToken(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem("jwt_token");
  }

  /**
   * Get authorization headers for API requests
   * @returns Headers object with JWT token
   */
  private getHeaders(): Headers {
    const token = this.getToken();
    const headers = new Headers({
      "Content-Type": "application/json",
    });

    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    return headers;
  }

  /**
   * Handle API errors
   * @param response - Fetch response object
   * @throws Error with appropriate message
   */
  private async handleError(response: Response): Promise<never> {
    if (response.status === 401) {
      // Redirect to login on unauthorized
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new Error(TaskAPIErrors.AUTH_REQUIRED);
    }

    if (response.status === 403) {
      throw new Error(TaskAPIErrors.PERMISSION_DENIED);
    }

    if (response.status === 404) {
      throw new Error(TaskAPIErrors.TASK_NOT_FOUND);
    }

    if (response.status >= 500) {
      throw new Error(TaskAPIErrors.SERVER_ERROR);
    }

    // Try to parse error response
    try {
      const error: APIError = await response.json();
      throw new Error(error.detail || TaskAPIErrors.SERVER_ERROR);
    } catch {
      throw new Error(TaskAPIErrors.SERVER_ERROR);
    }
  }

  /**
   * Fetch all tasks for the authenticated user
   * @returns List of tasks
   */
  async fetchTasks(): Promise<Task[]> {
    const response = await fetch(`${this.baseUrl}/api/tasks`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      if (response.status === 404) {
        // No tasks found - return empty array
        return [];
      }
      await this.handleError(response);
    }

    // Defensively handle API response - ensure we always return an array
    const data: unknown = await response.json();

    if (Array.isArray(data)) {
      return data as Task[];
    }

    if (data && typeof data === "object" && Array.isArray((data as { tasks?: unknown }).tasks)) {
      return (data as { tasks: Task[] }).tasks;
    }

    // Fallback: return empty array for unexpected response formats
    console.warn("Unexpected API response format from /tasks, expected array or {tasks: array}");
    return [];
  }

  /**
   * Create a new task
   * @param task - Task data with title (required) and description (optional)
   * @returns Created task
   */
  async createTask(task: TaskCreate): Promise<Task> {
    const response = await fetch(`${this.baseUrl}/api/tasks`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(task),
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    return await response.json();
  }

  /**
   * Update an existing task
   * @param id - Task ID
   * @param task - Updated task data
   * @returns Updated task
   */
  async updateTask(id: number, task: TaskUpdate): Promise<Task> {
    const response = await fetch(`${this.baseUrl}/api/tasks/${id}`, {
      method: "PUT",
      headers: this.getHeaders(),
      body: JSON.stringify(task),
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    return await response.json();
  }

  /**
   * Toggle task completion status
   * @param id - Task ID
   * @returns Updated task with toggled completion status
   */
  async toggleComplete(id: number): Promise<Task> {
    const response = await fetch(`${this.baseUrl}/api/tasks/${id}/complete`, {
      method: "PATCH",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    return await response.json();
  }

  /**
   * Delete a task
   * @param id - Task ID
   */
  async deleteTask(id: number): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/tasks/${id}`, {
      method: "DELETE",
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    // 204 No Content - no body to parse
  }
}

// Export singleton instance
export const tasks = new TaskService();
