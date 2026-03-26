function Sidebar({ tasks = [], setFilter, currentFilter }) {

  let active = 0;
  let done = 0;

  tasks.forEach((t) => {
    if (t.completed) done++;
    else active++;
  });

  const total = tasks.length;

  return (
    <div style={{
      background: "#111827",
      padding: "20px",
      borderRadius: "12px",
      color: "white",
      width: "200px"
    }}>

      <h3>Tasks</h3>

      <button
        style={{ marginBottom: "10px" }}
        className={currentFilter === "all" ? "active" : ""}
        onClick={() => setFilter("all")}
      >
        All ({total})
      </button>

      <button
        style={{ marginBottom: "10px" }}
        className={currentFilter === "active" ? "active" : ""}
        onClick={() => setFilter("active")}
      >
        Active ({active})
      </button>

      <button
        className={currentFilter === "done" ? "active" : ""}
        onClick={() => setFilter("done")}
      >
        Done ({done})
      </button>

    </div>
  );
}

export default Sidebar;