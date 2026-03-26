import { Trash2, Pencil } from "lucide-react";
import { motion } from "framer-motion";

function TaskCard({
  task,
  deleteTask,
  startEdit,
  updateTask,
  toggleTask,

  editingId,
  editingTitle,
  setEditingTitle
}) {

  return (

    <motion.div
      className="task-card"

      layout // 🔥 أهم سطر للأنيميشن

      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -40 }}

      transition={{
        duration: 0.25,
        type: "spring"
      }}
    >

      {/* LEFT SIDE */}
      <div className="task-left">

        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => toggleTask(task)}
        />

        <div className="task-content">

          {editingId === task.id ? (

            <>
              <input
                value={editingTitle}
                onChange={(e) => setEditingTitle(e.target.value)}

                // 🔥 Enter يحفظ
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    updateTask(task.id, editingTitle);
                  }
                }}
              />

              <button onClick={() => updateTask(task.id, editingTitle)}>
                Save
              </button>
            </>

          ) : (

            <>
              <span
                className={`task-title ${
                  task.completed ? "completed" : ""
                }`}
              >
                {task.title}
              </span>

              {/* 🔥 Priority Badge */}
              <span className={`badge ${task.priority}`}>
                {task.priority}
              </span>
            </>

          )}

        </div>

      </div>

      {/* RIGHT SIDE */}
      <div className="task-actions">

        {/* يظهر Edit فقط لو مش في وضع edit */}
        {editingId !== task.id && (
          <button onClick={() => startEdit(task)}>
            <Pencil size={16} />
          </button>
        )}

        <button onClick={() => deleteTask(task.id)}>
          <Trash2 size={16} />
        </button>

      </div>

    </motion.div>

  );

}

export default TaskCard;