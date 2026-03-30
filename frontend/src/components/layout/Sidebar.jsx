function Sidebar({ tasks = [], setFilter, currentFilter }) {
  const stats = tasks.reduce(
    (acc, t) => {
      if (t.completed) acc.done++;
      else acc.active++;
      acc.total++;
      return acc;
    },
    { total: 0, active: 0, done: 0 }
  );

  const filters = [
    { key: "all", label: "All", count: stats.total },
    { key: "active", label: "Active", count: stats.active },
    { key: "done", label: "Done", count: stats.done },
  ];

  return (
    <div className="h-full w-64 bg-gray-900 text-white p-5 flex flex-col">

      {/* Logo */}
      <h2 className="text-xl font-bold mb-6">TaskForge</h2>

      {/* Filters */}
      <div className="flex flex-col gap-2">

        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`flex justify-between items-center px-3 py-2 rounded-lg transition
              ${
                currentFilter === f.key
                  ? "bg-blue-600"
                  : "hover:bg-gray-800"
              }
            `}
          >
            <span>{f.label}</span>
            <span className="text-sm opacity-70">({f.count})</span>
          </button>
        ))}

      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Footer (جاهز للتوسعة) */}
      <div className="text-sm opacity-60">
        AI Task Manager 🚀
      </div>

    </div>
  );
}

export default Sidebar;