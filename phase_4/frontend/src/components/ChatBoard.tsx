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

interface Task {
  id: number;
  title: string;
  description: string;
  is_complete: boolean;
}


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


interface ChatBoardProps {
  className?: string;
}

const ChatBoard: React.FC<ChatBoardProps> = ({ className = '' }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [taskOperations, setTaskOperations] = useState<TaskOperation[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number>(0); // Start with 0 until first interaction
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, isAuthenticated } = useAuth();

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages, taskOperations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  





  // ✅ NEW FIXED FUNCTION
const executeMcpTools = async (operations: Array<{
  operation: string,
  status: 'success' | 'failed',
  error?: string,
  result?: { task?: Task; tasks?: Task[] },
  task_data?: any
}>) => {
  for (const op of operations) {
    const tempOpId = `temp-${Date.now()}-${Math.random()}`;

    // 🔹 backend ka real status use karo
    const taskData = op.status === 'failed'
      ? op.error
      : op.result?.task ?? op.result?.tasks ?? op.task_data ?? {};

    setTaskOperations(prev => [
      ...prev,
      {
        id: tempOpId,
        operation: op.operation,
        task_data: taskData,
        timestamp: new Date(),
        status: op.status === 'failed' ? 'error' : 'pending'
      }
    ]);

    // ❌ AGAR BACKEND FAILED → YAHIN RUK JAO
    if (op.status === 'failed') {
      setTaskOperations(prev =>
        prev.map(item =>
          item.id === tempOpId
            ? { ...item, status: 'error' }
            : item
        )
      );
      continue;
    }

    // ✅ SUCCESS CASE
    setTaskOperations(prev =>
      prev.map(item =>
        item.id === tempOpId
          ? { ...item, status: 'success' }
          : item
      )
    );

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
    <div className={`flex flex-col h-[calc(100vh-120px)] max-w-4xl mx-auto ${className}`}>
      {/* Header */}
      <div className="glass-card p-4 rounded-t-2xl flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">AI Todo Assistant</h2>
        <button
          onClick={handleClearChat}
          className="glass-button px-3 py-1.5 text-sm rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-600 border-red-500/30 transition-colors"
        >
          Clear Chat
        </button>
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
      <div className="p-3 whitespace-pre-wrap break-words max-h-40 overflow-auto">
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
            className={`glass-button px-4 py-2 rounded-xl flex items-center justify-center ${
              isLoading || !inputValue.trim() || !isAuthenticated
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
  );
};

export default ChatBoard;














