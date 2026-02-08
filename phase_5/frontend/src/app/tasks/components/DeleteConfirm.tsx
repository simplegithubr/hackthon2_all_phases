"use client";

/**
 * DeleteConfirm component - confirmation modal for deleting tasks
 * Client Component for interactivity
 */
import { useState } from "react";
import { Task } from "../../../types/tasks";

interface DeleteConfirmProps {
  task: Task;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function DeleteConfirm({
  task,
  onConfirm,
  onCancel,
}: DeleteConfirmProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-10">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Delete Task</h2>

        <p className="text-gray-600 mb-6">
          Are you sure you want to delete <strong>"{task.title}"</strong>?
          <br />
          This action cannot be undone.
        </p>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
