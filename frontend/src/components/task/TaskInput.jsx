import { useState } from "react";
import { generateSubtasks } from "../../services/aiService";

function TaskInput({ createTask }) {
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [subtasks, setSubtasks] = useState([]);

  const handleCreate = async () => {
  if (!title.trim()) {
    console.log("empty title create blocked");
    return;
  }

  setLoading(true);

  try {
    let finalSubtasks = subtasks;

    // 🔥 لو المستخدم مختارش generate manually
    if (subtasks.length === 0) {
      finalSubtasks = await generateSubtasks(title);
    }

    await createTask(title, finalSubtasks);

    setTitle("");
    setSubtasks([]);

  } catch (err) {
    console.error(err);
  } finally {
    setLoading(false);
  }
};
  const handleGenerate = async () => {
  if (!title.trim()) {
    console.log("❌ title is empty");
    return;
  }

  console.log("🔥 Generating subtasks for:", title);

  setLoading(true);
  try {
    const data = await generateSubtasks(title);
    console.log("🔥 AI RESULT:", data);

    setSubtasks(data);
  } catch (err) {
    console.error("AI error:", err);
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="bg-white p-4 rounded-xl shadow space-y-3">

      {/* Input */}
      <div className="flex gap-2">
        <input
          className="flex-1 p-2 border rounded-lg outline-none focus:ring-2 focus:ring-blue-400"
          type="text"
          placeholder="New task..."
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
        />

        <button
          onClick={handleCreate}
          disabled={!title.trim() || loading}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg disabled:opacity-50"
        >
          {loading ? "..." : "Create"}
        </button>
      </div>

      {/* AI Button */}
      <button
        onClick={handleGenerate}
        disabled={ loading}
        className="text-sm text-purple-600 hover:underline"
      >
        ✨ Generate subtasks
      </button>

      {/* Subtasks Preview */}
      {subtasks.length > 0 && (
        <ul className="text-sm bg-gray-50 p-2 rounded">
          {subtasks.map((sub, i) => (
            <li key={i}>• {sub}</li>
          ))}
        </ul>
      )}

    </div>
  );
}

export default TaskInput;