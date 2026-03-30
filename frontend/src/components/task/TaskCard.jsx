import { Trash2, Pencil } from "lucide-react";
import { motion } from "framer-motion";

function TaskCard({ task, actions, editing }) {
              console.log("task: ", task);
                  console.log("task.priority: ", task.priority);
  
  // ===============================
  // 🎯 Actions (وظائف التحكم)
  // ===============================
  const { deleteTask, startEdit, updateTask, toggleTask } = actions;

  // ===============================
  // ✏️ Editing State
  // ===============================
  const { editingId, editingTitle, setEditingTitle } = editing;
  
  // هل الكارت الحالي في وضع التعديل؟
  const isEditing = editingId === task.id;
  
  return (

    // ===============================
    // 🎬 Animation Wrapper (Framer Motion)
    // ===============================
    <motion.div
      layout // 🔥 يخلي العناصر تتحرك بسلاسة عند الإضافة/الحذف
      initial={{ opacity: 0, y: 15 }} // بداية الظهور
      animate={{ opacity: 1, y: 0 }}  // الحالة الطبيعية
      exit={{ opacity: 0, x: -40 }}   // عند الحذف
      transition={{ duration: 0.25, type: "spring" }}
      className="bg-white p-3 rounded-xl shadow flex justify-between items-start"
    >

      {/* ===============================
          🟢 LEFT SIDE (Content)
      =============================== */}
      <div className="flex gap-3 flex-1">

        {/* ✅ Checkbox */}
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => toggleTask(task)}
        />

        <div className="flex flex-col gap-1 w-full">

          {/* ===============================
              ✏️ EDIT MODE
          =============================== */}
          {isEditing ? (
            <div className="flex gap-2">

              {/* Input */}
              <input
                className="border rounded px-2 py-1 w-full"
                value={editingTitle}
                onChange={(e) => setEditingTitle(e.target.value)}

                // 🔥 Enter = Save
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    updateTask(task.id, editingTitle);
                  }
                }}
              />

              {/* Save Button */}
              <button
                onClick={() => updateTask(task.id, editingTitle)}
                className="text-sm text-blue-600"
              >
                Save
              </button>

            </div>
          ) : (

            // ===============================
            // 📄 VIEW MODE
            // ===============================
            <>
           <div className="flex items-center w-full gap-3">

            {/* Title */}
            <div
              className={`font-medium flex-1> min-w-0 `}
            >
              {task.title}
            </div>

            {/* Priority */}
            <div
              className={`px-2 py-1 text-xs ${
                task.priority === "low"
                  ? "bg-green-100 text-green-700"
                  : task.priority === "medium"
                  ? "bg-yellow-100 text-yellow-700"
                  : "bg-red-100 text-red-700"
              }`}
            >
              {task.priority.toUpperCase()}
            </div>

          </div>
              </>
            )}      

          {/* ===============================
              🌳 SUBTASKS (Recursive Tree)
          =============================== */}
          {task.subtasks && task.subtasks.length > 0 && (

            <div className="ml-4 border-l pl-3 mt-2 space-y-2">

              {task.subtasks.map((sub) => (

                // 🔥 Recursive Component
                <TaskCard
                  key={sub.id}
                  task={sub}
                  actions={actions}
                  editing={editing}
                />

              ))}

            </div>

          )}

        </div>
      </div>

      {/* ===============================
          🔴 RIGHT SIDE (Actions)
      =============================== */}
      <div className="flex gap-2">

        {/* ✏️ Edit Button */}
        {!isEditing && (
          <button
            onClick={() => startEdit(task)}
            className="text-gray-500 hover:text-blue-600"
          >
            <Pencil size={16} />
          </button>
        )}

        {/* 🗑️ Delete Button */}
        <button
          onClick={() => deleteTask(task.id)}
          className="text-gray-500 hover:text-red-600"
        >
          <Trash2 size={16} />
        </button>

      </div>
    </motion.div>
  );
}

export default TaskCard;