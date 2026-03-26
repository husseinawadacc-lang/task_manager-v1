import { useState } from "react";

function TaskInput({ createTask }) {

  const [title, setTitle] = useState("");

  const handleCreate = () => {

    if (!title.trim()) return;

    createTask(title);

    setTitle("");
  };

  return (

    <div style={{ display: "flex", gap: "10px" }}>

      <input
        style={{
          padding: "10px",
          borderRadius: "8px",
          border: "none",
          outline: "none",
          flex: 1
        }}
        type="text"
        placeholder="New task"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleCreate();
          }
        }}
      />

      <button
        disabled={!title.trim()}
        style={{
          padding: "10px 15px",
          borderRadius: "8px",
          background: "#3b82f6",
          color: "white",
          border: "none",
          cursor: "pointer",
          opacity: !title.trim() ? 0.5 : 1
        }}
        onClick={handleCreate}
      >
        Create
      </button>

    </div>

  );
}

export default TaskInput;