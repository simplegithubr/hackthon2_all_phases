"use client";

/**
 * AuthContext - Global authentication state management
 * Provides login, logout, and user state to all components
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { User } from "../types/auth";
import { auth } from "../services/auth";

/**
 * Auth context type definition
 */
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  signup: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

// Create context with undefined initial value
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component - wraps app and provides auth state
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check authentication status on mount
  useEffect(() => {
    function checkAuth() {
      if (auth.isAuthenticated()) {
        // Token exists - extract user info from token or storage
        // For now, just mark as authenticated
        setUser({ id: "", username: "User", created_at: new Date().toISOString() });
      }
      setIsLoading(false);
    }

    checkAuth();
  }, []);

  /**
   * Login user
   */
  const login = useCallback(async (username: string, password: string) => {
    setError(null);
    setIsLoading(true);

    try {
      await auth.login({ username, password });
      // Set a placeholder user - backend doesn't return user info on login
      setUser({ id: "", username, created_at: new Date().toISOString() });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Register new user
   */
  const signup = useCallback(async (username: string, password: string) => {
    setError(null);
    setIsLoading(true);

    try {
      await auth.signup({ username, password });
      // Set a placeholder user - backend doesn't return user info on signup
      setUser({ id: "", username, created_at: new Date().toISOString() });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Signup failed";
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(async () => {
    setError(null);
    try {
      await auth.logout();
      setUser(null);
    } catch {
      // Even if logout fails, clear local state
      setUser(null);
      auth.clearToken();
    }
  }, []);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: auth.isAuthenticated(),
    login,
    signup,
    logout,
    error,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Custom hook to use auth context
 * @returns Auth context value
 * @throws Error if used outside AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

/**
 * Custom hook to get current user
 * @returns User object or null if not authenticated
 */
export function useUser() {
  const { user, isLoading, isAuthenticated } = useAuth();
  return { user, isLoading, isAuthenticated };
}

/**
 * Custom hook to require authentication
 * Redirects to login if not authenticated
 */
export function useRequireAuth() {
  const { user, isLoading, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Redirect to login
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
  }, [isLoading, isAuthenticated]);

  return { user, isLoading, isAuthenticated };
}
