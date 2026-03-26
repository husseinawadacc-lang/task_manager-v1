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

  // =========================
  // 🟥 Empty State هنا
  // =========================
  if (tasks.length === 0) {
    return (
      <div style={{ textAlign: "center", marginTop: "40px" }}>
        <h3>📭 No tasks yet</h3>
        <p style={{ opacity: 0.6 }}>
          Start by creating your first task 🚀
        </p>
      </div>
    );
  }

  // =========================
  // 🟩 عرض المهام
  // =========================
  return (

    <div>

  <AnimatePresence mode="popLayout">
    
    {tasks.map((task) => (

        <TaskCard
            key={task.id}
            task={task}
            deleteTask={deleteTask}
            startEdit={startEdit}
            updateTask={updateTask}
            toggleTask={toggleTask}
            editingId={editingId}
            editingTitle={editingTitle}
            setEditingTitle={setEditingTitle}
          />

      ))}
    </AnimatePresence>
    </div>
  );

}

export default TaskList;