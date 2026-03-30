import TaskCard from "./TaskCard";
import { AnimatePresence } from "framer-motion";

function TaskList({
  tasks,
  deleteTask,
  startEdit,
  updateTask,
  toggleTask,
  editingId,
  editingTitle,
  setEditingTitle,
}) {

  // 🟥 Empty State
  if (!tasks || tasks.length === 0) {
    return (
      <div className="text-center mt-10 text-gray-500">
        <h3 className="text-lg font-semibold">📭 No tasks yet</h3>
        <p className="text-sm opacity-70">
          Start by creating your first task 🚀
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">

      <AnimatePresence mode="popLayout">

        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}

            // 🔥 actions grouped
            actions={{
              deleteTask,
              startEdit,
              updateTask,
              toggleTask,
            }}

            editing={{
              editingId,
              editingTitle,
              setEditingTitle,
            }}
          />
        ))}

      </AnimatePresence>

    </div>
  );
}

export default TaskList;