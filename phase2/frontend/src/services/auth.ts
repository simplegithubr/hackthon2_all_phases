/**
 * Auth API service for communicating with backend authentication endpoints
 * Provides type-safe methods for login, signup, and token management
 */
import {
  User,
  LoginRequest,
  LoginResponse,
  SignupRequest,
  SignupResponse,
  APIError,
  AuthAPIErrors,
} from "../types/auth";

/**
 * AuthService class for managing authentication API calls
 */
export class AuthService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "https://sagardeveloper-todo-phase2.hf.space";
  }

  /**
   * Get JWT token from localStorage
   * @returns JWT token or null if not found
   */
  public getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("jwt_token");
  }

  /**
   * Set JWT token in localStorage
   * @param token - JWT token from authentication
   */
  public setToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("jwt_token", token);
  }

  /**
   * Clear JWT token from localStorage
   */
  public clearToken(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem("jwt_token");
  }

  /**
   * Check if user is authenticated
   * @returns true if token exists
   */
  public isAuthenticated(): boolean {
    return this.getToken() !== null;
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
      throw new Error(AuthAPIErrors.INVALID_CREDENTIALS);
    }

    if (response.status === 403) {
      throw new Error(AuthAPIErrors.AUTH_REQUIRED);
    }

    if (response.status === 409) {
      throw new Error(AuthAPIErrors.USER_EXISTS);
    }

    if (response.status >= 500) {
      throw new Error(AuthAPIErrors.SERVER_ERROR);
    }

    // Try to parse error response
    try {
      const error: APIError = await response.json();
      throw new Error(error.detail || AuthAPIErrors.SERVER_ERROR);
    } catch {
      throw new Error(AuthAPIErrors.SERVER_ERROR);
    }
  }

  /**
   * Login user with username and password
   * @param credentials - Login credentials
   * @returns Login response with token
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    const data: LoginResponse = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  /**
   * Register new user
   * @param data - Signup data
   * @returns Signup response with token
   */
  async signup(data: SignupRequest): Promise<SignupResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: data.username, password: data.password }),
    });

    if (!response.ok) {
      await this.handleError(response);
    }

    const result: SignupResponse = await response.json();
    this.setToken(result.access_token);
    return result;
  }

  /**
   * Logout user - clears token locally
   * Note: Backend JWT tokens are stateless, so we just clear locally
   */
  async logout(): Promise<void> {
    this.clearToken();
  }
}

// Export singleton instance
export const auth = new AuthService();
