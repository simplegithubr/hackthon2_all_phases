/**
 * WebSocket Client for Real-Time Task Updates
 * Connects to WebSocket service and receives live task updates
 */

import React from 'react';

type TaskUpdateEvent = {
  event_type: 'task.created' | 'task.updated' | 'task.completed' | 'task.deleted';
  user_id: string;
  task_id: string;
  title?: string;
  description?: string;
  priority?: string;
  updated_fields?: Record<string, any>;
  timestamp: string;
};

type WebSocketMessage = {
  type: 'connected' | 'task_update' | 'pong';
  message?: string;
  event?: TaskUpdateEvent;
  timestamp: string;
};

type WebSocketClientOptions = {
  url: string;
  userId: string;
  token?: string;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onTaskUpdate?: (event: TaskUpdateEvent) => void;
  onError?: (error: Error) => void;
  reconnectInterval?: number;
};

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private options: WebSocketClientOptions;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingTimer: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private shouldReconnect = true;

  constructor(options: WebSocketClientOptions) {
    this.options = {
      reconnectInterval: 5000,
      ...options,
    };
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connected or connecting');
      return;
    }

    this.isConnecting = true;
    this.shouldReconnect = true;

    try {
      // Build WebSocket URL with query params
      const url = new URL(this.options.url);
      url.searchParams.set('user_id', this.options.userId);
      if (this.options.token) {
        url.searchParams.set('token', this.options.token);
      }

      console.log('Connecting to WebSocket:', url.toString());
      this.ws = new WebSocket(url.toString());

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.shouldReconnect = false;
    this.clearTimers();

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen(): void {
    console.log('✓ WebSocket connected');
    this.isConnecting = false;

    // Start ping timer to keep connection alive
    this.startPingTimer();

    if (this.options.onConnect) {
      this.options.onConnect();
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'connected':
          console.log('WebSocket connection confirmed:', message.message);
          break;

        case 'task_update':
          if (message.event && this.options.onTaskUpdate) {
            console.log('📡 Task update received:', message.event.event_type);
            this.options.onTaskUpdate(message.event);
          }
          break;

        case 'pong':
          // Pong received, connection is alive
          break;

        default:
          console.log('Unknown message type:', message);
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  /**
   * Handle WebSocket error
   */
  private handleError(event: Event): void {
    console.error('WebSocket error:', event);

    if (this.options.onError) {
      this.options.onError(new Error('WebSocket error'));
    }
  }

  /**
   * Handle WebSocket close event
   */
  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason);
    this.isConnecting = false;
    this.clearTimers();

    if (this.options.onDisconnect) {
      this.options.onDisconnect();
    }

    // Attempt to reconnect if not manually disconnected
    if (this.shouldReconnect) {
      this.scheduleReconnect();
    }
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return;
    }

    console.log(`Reconnecting in ${this.options.reconnectInterval}ms...`);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, this.options.reconnectInterval);
  }

  /**
   * Start ping timer to keep connection alive
   */
  private startPingTimer(): void {
    this.pingTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping' });
      }
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Clear all timers
   */
  private clearTimers(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  /**
   * Send message to WebSocket server
   */
  private send(data: any): void {
    if (this.isConnected() && this.ws) {
      this.ws.send(JSON.stringify(data));
    }
  }
}

/**
 * React Hook for WebSocket connection
 */
export function useWebSocket(options: Omit<WebSocketClientOptions, 'url'>) {
  const [isConnected, setIsConnected] = React.useState(false);
  const clientRef = React.useRef<WebSocketClient | null>(null);

  React.useEffect(() => {
    // Get WebSocket URL from environment or default
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8004/ws';

    // Create WebSocket client
    clientRef.current = new WebSocketClient({
      url: wsUrl,
      ...options,
      onConnect: () => {
        setIsConnected(true);
        options.onConnect?.();
      },
      onDisconnect: () => {
        setIsConnected(false);
        options.onDisconnect?.();
      },
    });

    // Connect
    clientRef.current.connect();

    // Cleanup on unmount
    return () => {
      if (clientRef.current) {
        clientRef.current.disconnect();
      }
    };
  }, [options.userId, options.token]);

  return {
    isConnected,
    client: clientRef.current,
  };
}

export default WebSocketClient;
