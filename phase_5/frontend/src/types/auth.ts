// TypeScript type definitions for Authentication feature
// JWT-based authentication with FastAPI backend

/**
 * User entity representing authenticated user
 */
export interface User {
  id: string;
  username: string;
  created_at: string;  // ISO 8601 datetime string
  email?: string;      // Optional email field from backend
}

/**
 * Login request body
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * Login response from backend
 */
export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
}

/**
 * Signup request body
 */
export interface SignupRequest {
  username: string;
  password: string;
  confirmPassword?: string;  // Client-side only, not sent to API
}

/**
 * Signup response from backend
 */
export interface SignupResponse {
  access_token: string;
  token_type: "bearer";
}

/**
 * Standard error response from API
 */
export interface APIError {
  detail: string;
}

/**
 * HTTP status codes for auth API responses
 */
export const AuthAPIStatus = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  CONFLICT: 409,
  INTERNAL_SERVER_ERROR: 500,
} as const;

/**
 * Error detail messages from API
 */
export const AuthAPIErrors = {
  INVALID_USERNAME: "Username must be 3-50 characters",
  INVALID_PASSWORD: "Password must be at least 6 characters",
  INVALID_CREDENTIALS: "Invalid username or password",
  USERNAME_REQUIRED: "Username is required",
  PASSWORD_REQUIRED: "Password is required",
  USER_EXISTS: "Username already registered",
  AUTH_REQUIRED: "Authentication required",
  SERVER_ERROR: "Something went wrong. Please try again.",
  PASSWORDS_DONT_MATCH: "Passwords do not match",
  WEAK_PASSWORD: "Password must be at least 6 characters long",
} as const;

/**
 * Validation rules for authentication (frontend)
 */
export const AuthValidation = {
  MIN_PASSWORD_LENGTH: 6,
  MIN_USERNAME_LENGTH: 3,
  MAX_USERNAME_LENGTH: 50,
} as const;

/**
 * Helper function to validate username
 * @returns true if valid, error message if invalid
 */
export function validateUsername(username: string): true | string {
  if (!username || username.trim().length === 0) {
    return AuthAPIErrors.USERNAME_REQUIRED;
  }
  if (username.length < AuthValidation.MIN_USERNAME_LENGTH) {
    return AuthAPIErrors.INVALID_USERNAME;
  }
  if (username.length > AuthValidation.MAX_USERNAME_LENGTH) {
    return AuthAPIErrors.INVALID_USERNAME;
  }
  return true;
}

/**
 * Helper function to validate password
 * @returns true if valid, error message if invalid
 */
export function validatePassword(password: string): true | string {
  if (!password || password.length === 0) {
    return AuthAPIErrors.PASSWORD_REQUIRED;
  }
  if (password.length < AuthValidation.MIN_PASSWORD_LENGTH) {
    return AuthAPIErrors.WEAK_PASSWORD;
  }
  return true;
}

/**
 * Helper function to validate password confirmation
 * @returns true if valid, error message if invalid
 */
export function validatePasswordConfirmation(
  password: string,
  confirmPassword: string
): true | string {
  if (password !== confirmPassword) {
    return AuthAPIErrors.PASSWORDS_DONT_MATCH;
  }
  return true;
}
