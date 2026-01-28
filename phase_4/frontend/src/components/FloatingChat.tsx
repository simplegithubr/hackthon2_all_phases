'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

// Define TypeScript interfaces
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface TaskOperation {
  id: string;
  operation: string;
  task_data?: any;
  timestamp: Date;
  status: 'pending' | 'success' | 'error';
}

interface Task {
  id: number;
  title: string;
  description: string;
  is_complete: boolean;
}

// Component to display tasks from list_tasks operation
const TasksDisplay: React.FC<{ tasks: Task[] }> = ({ tasks }) => {
  if (!tasks || tasks.length === 0) {
    return (
      <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-700 text-sm">No tasks found.</p>
      </div>
    );
  }

  return (
    <div className="mt-2 space-y-2">
      <h4 className="font-medium text-gray-700">Tasks:</h4>
      <div className="space-y-2 max-h-60 overflow-y-auto">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`p-3 rounded-lg border shadow-sm ${task.is_complete
              ? 'bg-green-100 border-green-300 text-green-800'
              : 'bg-orange-50 border-orange-200 text-orange-800'
              }`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1 min-w-0">
                <h5 className="font-medium truncate">{task.title}</h5>
                {task.description && (
                  <p className="text-sm mt-1 truncate">{task.description}</p>
                )}
              </div>
              <span className={`ml-2 px-2 py-1 text-xs rounded-full font-medium ${task.is_complete
                ? 'bg-green-200 text-green-800'
                : 'bg-orange-200 text-orange-800'
                }`}>
                {task.is_complete ? 'Completed' : 'Pending'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};


interface ChatApiResponse {
  response: string;
  conversation_id: number;
  task_operations: Array<{
    operation: string;
    status: 'success' | 'failed';
    error?: string;
    result?: {
      task?: Task;
      tasks?: Task[];
    };
    task_data?: any;
  }>;
}


const FloatingChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [taskOperations, setTaskOperations] = useState<TaskOperation[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number>(0); // Start with 0 until first interaction
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, isAuthenticated } = useAuth();

  // Toggle chat window
  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // Close chat window
  const closeChat = () => {
    setIsOpen(false);
  };

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages, taskOperations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };




 
  const executeMcpTools = async (operations: Array<{
    operation: string,
    status: 'success' | 'failed',
    error?: string,
    result?: { task?: Task; tasks?: Task[] },
    arguments?: any,
    task_data?: any
  }>) => {
    for (const op of operations) {
      const tempOpId = `temp-${Date.now()}-${Math.random()}`;

      // 🔹 Safe task_data assignment
      const taskData = op.status === 'failed'
        ? op.error
        : op.result?.task ?? op.result?.tasks ?? op.arguments ?? op.task_data ?? {};

      // 🔹 Add task operation to state
      setTaskOperations(prev => [
        ...prev,
        {
          id: tempOpId,
          operation: op.operation,
          task_data: taskData,
          timestamp: new Date(),
          status: op.status === 'failed' ? 'error' : 'success',
        }
      ]);

      // 🔹 Handle task completion updates immediately
      if (op.operation === 'complete_task' && op.status === 'success' && op.result?.task) {
        setMessages(prev => {
          const newMessages = [...prev];
          // Find and update any related messages if needed
          return newMessages;
        });
      }
    }
  };





  // Handle sending a message
  const handleSend = async () => {
    if (!inputValue.trim() || isLoading || !isAuthenticated) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    // Add user message to state immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get JWT token from auth context
      const token = localStorage.getItem('jwt_token');

      if (!token) {
        throw new Error('No authentication token found');
      }

      // Prepare request payload
      const requestBody = {
        message: userMessage.text,
        conversation_id: conversationId,
      };

    
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/chat`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }


      const data: ChatApiResponse = await response.json();

      // Update conversation ID if received
      if (data.conversation_id !== undefined) {
        setConversationId(data.conversation_id);
      }

      // Process task operations if any
      if (data.task_operations && data.task_operations.length > 0) {
        // Execute MCP tools for each operation (this will update the task operations state)
        await executeMcpTools(data.task_operations);
      }

      // Add bot response to messages
      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        text: data.response,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to chat
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle key press (Enter to send, Shift+Enter for new line)
  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Delete a single message or task operation
  const handleDeleteItem = (id: string, type: 'message' | 'task') => {
    if (type === 'message') {
      setMessages(prev => prev.filter(msg => msg.id !== id));
    } else {
      setTaskOperations(prev => prev.filter(op => op.id !== id));
    }
  };

  // Clear entire chat
  const handleClearChat = () => {
    setMessages([]);
    setTaskOperations([]);
    setConversationId(0); // Reset conversation ID
  };

  return (
    <>
      {/* Floating Chat Icon */}
      {!isOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-8 right-8 z-50 w-16 h-16 rounded-full bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-opacity-50"
          aria-label="Open chat"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="w-8 h-8"
          >
            <path d="M4.913 2.658c2.075-.27 4.19-.408 6.337-.408 2.147 0 4.262.139 6.337.408 1.922.25 3.291 1.861 3.405 3.727a4.403 4.403 0 00-1.032-.211 50.89 50.89 0 00-8.42 0c-2.358.196-4.04 2.19-4.04 4.434v4.286a4.47 4.47 0 002.433 3.984L7.28 21.53A.75.75 0 016 21v-4.03a48.527 48.527 0 01-1.087-.128C2.905 16.58 1.5 14.833 1.5 12.862V6.638c0-1.97 1.405-3.718 3.413-3.979z" />
            <path d="M15.75 7.5c-1.376 0-2.739.057-4.086.169C10.124 7.797 9 9.103 9 10.609v4.285c0 1.507 1.128 2.814 2.67 2.94 1.243.102 2.5.157 3.768.165l2.782 2.781a.75.75 0 001.28-.53v-2.39l.33-.026c1.542-.125 2.67-1.433 2.67-2.94v-4.286c0-1.505-1.125-2.811-2.664-2.94A49.392 49.392 0 0015.75 7.5z" />
          </svg>
        </button>
      )}

      {/* Chat Popup Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-end justify-end p-4 sm:p-6 pointer-events-none">
          <div
            className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
            onClick={closeChat}
          ></div>

          {/* Chat Window */}
          <div
            className="relative w-full max-w-md h-[600px] max-h-[80vh] glass-card rounded-2xl shadow-2xl flex flex-col pointer-events-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="glass-card p-4 rounded-t-2xl flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-800">AI Todo Assistant</h2>
              <div className="flex space-x-2">
                <button
                  onClick={handleClearChat}
                  className="glass-button px-3 py-1.5 text-sm rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-600 border-red-500/30 transition-colors"
                >
                  Clear
                </button>
                <button
                  onClick={closeChat}
                  className="glass-button w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-200 transition-colors"
                  aria-label="Close chat"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Messages and Task Operations Container */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white/10 backdrop-blur-sm rounded-b-2xl">
              {messages.length === 0 && taskOperations.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-500 italic">
                  Start a conversation with the AI assistant...
                </div>
              ) : (
                <>
                  {/* Render messages */}
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] relative group ${message.sender === 'user'
                          ? 'bg-violet-500 text-white rounded-br-none rounded-2xl'
                          : 'bg-white/80 text-gray-800 rounded-bl-none rounded-2xl'}`}
                      >
                        <div className="p-3 whitespace-pre-wrap break-words">
                          {message.text}
                        </div>

                        {/* Delete button - for all messages and visible on hover */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteItem(message.id, 'message');
                          }}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity shadow-md hover:bg-red-600 z-10"
                          aria-label="Delete message"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  ))}

                  {/* Render task operations */}
                  {taskOperations.map((operation) => {
                    const data = operation.task_data;

                    // Check if task exists
                    const hasTask =
                      data && typeof data === 'object' && 'id' in data;

                return (
  <div key={operation.id} className="flex justify-center">
    <div
      className={`max-w-[80%] relative group bg-blue-100 text-blue-800 rounded-2xl border-l-4 ${
        operation.status === 'success'
          ? 'border-green-500'
          : operation.status === 'error'
          ? 'border-red-500'
          : 'border-blue-500'
      }`}
    >
      <div className="p-3 whitespace-pre-wrap break-words max-h-60 overflow-auto">
        <div className="font-medium capitalize">
          {operation.operation.replace('_', ' ')}:
        </div>

        {/* Render error if failed */}
        {operation.status === 'error' && (
          <pre className="text-xs mt-1 text-red-600 break-words whitespace-pre-wrap">
            {JSON.stringify(data, null, 2)}
          </pre>
        )}

        {/* Render task info if success and task exists */}
        {operation.status === 'success' && hasTask && (
          <div className="mt-1 text-sm text-gray-700">
            <p><strong>Task ID:</strong> {data.id}</p>
            {data.user_id && <p><strong>User ID:</strong> {data.user_id}</p>}
            {data.title && <p><strong>Title:</strong> {data.title}</p>}
            {data.description && <p><strong>Description:</strong> {data.description}</p>}
            {typeof data.is_complete === 'boolean' && (
              <p>
                <strong>Status:</strong>
                <span className={`ml-1 px-2 py-1 text-xs rounded-full font-medium ${
                  data.is_complete
                    ? 'bg-green-200 text-green-800'
                    : 'bg-orange-200 text-orange-800'
                }`}>
                  {data.is_complete ? 'Completed' : 'Pending'}
                </span>
              </p>
            )}
          </div>
        )}

        {/* If no task and success but some other data */}
        {operation.status === 'success' && !hasTask && data && (
          <pre className="text-xs mt-1 break-words whitespace-pre-wrap max-h-40 overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        )}

        <div className="text-xs mt-1 opacity-70">
          {operation.status === 'success'
            ? '✓ Success'
            : operation.status === 'error'
            ? '✗ Error'
            : 'Processing...'}
        </div>
      </div>

      {/* Delete button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          handleDeleteItem(operation.id, 'task');
        }}
        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity shadow-md hover:bg-red-600 z-10"
        aria-label="Delete task operation"
      >
        ×
      </button>
    </div>
  </div>
);

                  })}

                </>
              )}

              {/* Loading indicator when bot is typing */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/80 text-gray-800 rounded-2xl rounded-bl-none p-3 max-w-[80%]">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="glass-card p-4 mt-4 rounded-2xl">
              <div className="flex gap-2">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Type your message..."
                  className="glass-input flex-1 resize-none py-2 px-4 rounded-xl min-h-[60px] max-h-32 focus:outline-none focus:ring-2 focus:ring-violet-500"
                  rows={1}
                  disabled={isLoading || !isAuthenticated}
                />
                <button
                  onClick={handleSend}
                  disabled={isLoading || !inputValue.trim() || !isAuthenticated}
                  className={`glass-button px-4 py-2 rounded-xl flex items-center justify-center ${isLoading || !inputValue.trim() || !isAuthenticated
                    ? 'opacity-50 cursor-not-allowed'
                    : 'hover:bg-white/90'
                    }`}
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="w-5 h-5 text-violet-600"
                  >
                    <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
                  </svg>
                </button>
              </div>
              {!isAuthenticated && (
                <p className="text-sm text-red-500 mt-2 text-center">
                  Please log in to use the chat
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingChat;