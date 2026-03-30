// =======================================
// Dashboard.jsx (Clean SaaS Version)
// =======================================

import { useEffect, useState } from "react";

// 🧠 Services (بدل api مباشرة)
import {
  getTasks,
  createTask as createTaskAPI,
  updateTask as updateTaskAPI,
  deleteTask as deleteTaskAPI,
} from "../services/taskService";

import {
  getProjects,
  createProject as createProjectAPI,
  deleteProject as deleteProjectAPI,
} from "../services/projectService";

// 🧩 Components
import Sidebar from "../components/layout/Sidebar";
import TaskInput from "../components/task/TaskInput";
import TaskList from "../components/task/TaskList";

import toast from "react-hot-toast";

function Dashboard() {

  // ===============================
  // 🎯 STATE MANAGEMENT
  // ===============================

  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);

  const [selectedProject, setSelectedProject] = useState(null);

  const [loading, setLoading] = useState(true);

  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");

  // ===============================
  // 📦 FETCH PROJECTS
  // ===============================
  const fetchProjects = async () => {
    
      const data = await getProjects();

      setProjects(data);

  };

  // ===============================
  // 📦 FETCH TASKS
  // ===============================
  const fetchTasks = async () => {
    console.log("Fetching tasks for project:", selectedProject);
    if (!selectedProject) return;

    setLoading(true);

    try {
      const data = await getTasks(selectedProject);

      // API بيرجع { items, total }
      setTasks(data.items);

    } catch {
      toast.error("Failed to load tasks ❌");
    } finally {
      setLoading(false);
    }
  };
  // ===============================
  // ⚙️ EFFECTS (Lifecycle)
  // ===============================

  // أول تحميل (تحميل المشاريع)
  useEffect(() => {
    fetchProjects();
  }, []);

  // 🔥 هنا تحط الكود ده 👇
  useEffect(() => {
    if (!selectedProject && projects.length > 0) {
      setSelectedProject(projects[0].id);
    }
  }, [projects]);

  // لما project يتغير → نجيب tasks
  useEffect(() => {
    fetchTasks();
}, [selectedProject]);
  // ===============================
  // 🧠 PROJECT ACTIONS
  // ===============================

  const createProject = async () => {
    const name = prompt("Project name");

    if (!name?.trim()) return;

    try {
      await createProjectAPI({ name });

      toast.success("Project created 🚀");

      await fetchProjects();

    } catch {
      toast.error("Create project failed ❌");
    }
  };

  const deleteProject = async () => {
    if (!selectedProject) return;

    if (!window.confirm("Delete this project?")) return;

    try {
      await deleteProjectAPI(selectedProject);

      toast.success("Project deleted 🗑️");

      await fetchProjects();

    } catch {
      toast.error("Delete failed ❌");
    }
  };

  // ===============================
  // 🧠 TASK ACTIONS
  // ===============================
  const createTask = async (title, subtasks = []) => {
  console.log("DASHBOARD createTask 🔥", title, subtasks);

  if (!selectedProject) {
    toast.error("Select project first");
    return;
  }

  try {
    // 1️⃣ create main task
    console.log("Creating main task...");
    const created = await createTaskAPI({
      title,
      description: "",
      project_id: selectedProject,
    });
    console.log("Main task created:", created);
    // 2️⃣ لو في subtasks → اعملهم
    for (const sub of subtasks) {
      await createTaskAPI({
        title: sub,
        description: "",
        project_id: selectedProject,
        parent_id: created.id,
      });
    }

    toast.success("Task created ✅");

    // 🔥 مهم جدًا
    setTasks(prev => [...prev, subtasks]);

    // 🔥 رجع قيمة
    return created;

  } catch (err) {
    console.error(err);
    toast.error("Create failed ❌");
    throw err;
  }
};


  const updateTask = async (id, title) => {
    try {
      await updateTaskAPI(id, { title });

      // تحديث local state بدون reload
      setTasks(prev =>
        prev.map(t => t.id === id ? { ...t, title } : t)
      );

      setEditingId(null);
      setEditingTitle("");

    } catch {
      toast.error("Update failed ❌");
    }
  };

  const deleteTask = async (id) => {
    await deleteTaskAPI(id);
    fetchTasks();
  };

  const toggleTask = async (task) => {
    await updateTaskAPI(task.id, {
      completed: !task.completed
    });
    await fetchTasks();
  };

  // ===============================
  // 🔍 FILTER + SEARCH
  // ===============================

  const filteredTasks = tasks.filter((t) => {

    // filter
    if (filter === "active" && t.completed) return false;
    if (filter === "done" && !t.completed) return false;

    // search
    return t.title.toLowerCase().includes(search.toLowerCase());
  });

  // ===============================
  // 🧱 UI
  // ===============================

  return (
    <div className="flex h-screen bg-gray-100">

      {/* ===============================
          🟦 SIDEBAR
      =============================== */}
      <Sidebar
        tasks={tasks}
        setFilter={setFilter}
        currentFilter={filter}
      />

      {/* ===============================
          🟩 MAIN CONTENT
      =============================== */}
      <div className="flex-1 p-6 overflow-auto">

        {/* 🔝 HEADER */}
        <div className="flex justify-between items-center mb-6">

          <h1 className="text-2xl font-bold">TaskForge ⚒️</h1>

          <button
            onClick={() => {
              localStorage.removeItem("token");
              window.location.href = "/";
            }}
            className="text-sm text-red-500"
          >
            Logout
          </button>

        </div>

        {/* 📁 PROJECT BAR */}
        <div className="flex gap-2 mb-4">

          <select
            className="border p-2 rounded-lg"
            value={selectedProject || ""}
            onChange={(e) => setSelectedProject(Number(e.target.value))}
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                📁 {p.name}
              </option>
            ))}
          </select>

          <button
            onClick={createProject}
            className="px-3 py-2 bg-blue-500 text-white rounded-lg"
          >
            + New
          </button>

          {selectedProject && (
            <button
              onClick={deleteProject}
              className="px-3 py-2 bg-red-500 text-white rounded-lg"
            >
              🗑️
            </button>
          )}

        </div>

        {/* 🔍 SEARCH */}
        <input
          className="border p-2 rounded-lg w-full mb-4"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {/* ➕ CREATE TASK */}
        <TaskInput createTask={createTask} />

        {/* 📭 EMPTY */}
        {filteredTasks.length === 0 && (
          <p className="mt-4 text-gray-500">No tasks yet 🚀</p>
        )}

        {/* 📋 TASK LIST */}
        <TaskList
          tasks={filteredTasks}
          deleteTask={deleteTask}
          startEdit={(t) => {
            setEditingId(t.id);
            setEditingTitle(t.title);
          }}
          updateTask={updateTask}
          toggleTask={toggleTask}
          editingId={editingId}
          editingTitle={editingTitle}
          setEditingTitle={setEditingTitle}
        />

      </div>
    </div>
  );
}

export default Dashboard;