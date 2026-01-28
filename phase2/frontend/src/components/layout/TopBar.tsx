"use client";

interface TopBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  activeFilter: string;
  onFilterChange: (filter: string) => void;
  totalTasks: number;
  sortBy?: string;
  onSortChange?: (sort: string) => void;
  priority?: string;
  onPriorityChange?: (priority: string) => void;
}

const filters = [
  { name: "All", value: "all" },
  { name: "Active", value: "active" },
  { name: "Completed", value: "completed" },
];

const sortOptions = [
  { name: "Newest First", value: "newest" },
  { name: "Oldest First", value: "oldest" },
  { name: "By Title", value: "title" },
];

const priorityOptions = [
  { name: "All", value: "all" },
  { name: "High", value: "high" },
  { name: "Medium", value: "medium" },
  { name: "Low", value: "low" },
];

export default function TopBar({
  searchQuery,
  onSearchChange,
  activeFilter,
  onFilterChange,
  totalTasks,
  sortBy = "newest",
  onSortChange,
  priority = "all",
  onPriorityChange,
}: TopBarProps) {
  return (
    <div className="glass sticky top-0 z-30 rounded-2xl mb-6">
      <div className="p-6">
        {/* Search and Title Row */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">My Tasks</h1>
            <p className="text-sm text-gray-500">{totalTasks} task{totalTasks !== 1 ? "s" : ""}</p>
          </div>

          {/* Search Input */}
          <div className="relative w-64">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-xl glass-input text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-400/50"
            />
          </div>
        </div>

        {/* Filter Tabs, Priority, and Sort */}
        <div className="flex items-center gap-3 flex-wrap">
          {/* Filter Tabs */}
          <div className="flex items-center gap-1 p-1.5 rounded-xl bg-white/50 backdrop-blur-sm">
            {filters.map((filter) => (
              <button
                key={filter.value}
                onClick={() => onFilterChange(filter.value)}
                className={`px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeFilter === filter.value
                    ? "bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-lg"
                    : "text-gray-600 hover:bg-white/80 hover:text-gray-800"
                }`}
              >
                {filter.name}
              </button>
            ))}
          </div>

          {/* Priority Filter */}
          {onPriorityChange && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">Priority:</span>
              <select
                value={priority}
                onChange={(e) => onPriorityChange(e.target.value)}
                className="px-4 py-2.5 rounded-lg glass-input text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-violet-400/50 cursor-pointer"
              >
                {priorityOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Sort */}
          {onSortChange && (
            <div className="flex items-center gap-2 ml-auto">
              <span className="text-sm text-gray-500">Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => onSortChange(e.target.value)}
                className="px-4 py-2.5 rounded-lg glass-input text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-violet-400/50 cursor-pointer"
              >
                {sortOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
