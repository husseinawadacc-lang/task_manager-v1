// ===============================
// Dashboard.jsx (FINAL CLEAN VERSION)
// ===============================

import { useEffect, useState, useRef } from "react";
import api from "../api/api";
import TaskInput from "../components/TaskInput";
import TaskList from "../components/TaskList";
import Sidebar from "../components/Sidebar";
import toast from "react-hot-toast";

function Dashboard() {

  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");

  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);

  const searchRef = useRef(null);

  // ===============================
  // FETCH TASKS
  // ===============================
  const fetchTasks = async () => {
    if (!selectedProject) return;

    setLoading(true);

    try {
      const res = await api.get(`/tasks?project_id=${selectedProject}`);
      setTasks(res.data.items);
    } catch (err) {
      toast.error("Failed to load tasks ❌");
    } finally {
      setLoading(false);
    }
  };

  // ===============================
  // FETCH PROJECTS
  // ===============================
  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects");
      setProjects(res.data);

      const exists = res.data.find(p => p.id === selectedProject);

      if (!exists && res.data.length > 0) {
        setSelectedProject(res.data[0].id);
      }

    } catch (err) {
      console.log(err);
    }
  };

  // ===============================
  // CREATE PROJECT
  // ===============================
  const createProject = async () => {
    const name = prompt("Project name");

    if (!name || name.trim() === "") return;

    try {
      await api.post("/projects", { name });

      const res = await api.get("/projects");
      setProjects(res.data);

      // select new project
      setSelectedProject(res.data[res.data.length - 1].id);

      toast.success("Project created 🚀");

    } catch {
      toast.error("Create project failed ❌");
    }
      toast.error ("Project name already exists ❌ ");

  
  };

  // ===============================
  // DELETE PROJECT 🔥
  // ===============================
  const deleteProject = async () => {
    if (!selectedProject) return;

    const confirmDelete = window.confirm("Delete this project?");

    if (!confirmDelete) return;

    try {
      await api.delete(`/projects/${selectedProject}`);

      toast.success("Project deleted 🗑️");

      await fetchProjects(); // reload projects

    } catch {
      toast.error("Delete failed ❌");
    }
  };

  // ===============================
  // EFFECTS
  // ===============================
  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) fetchTasks();
  }, [selectedProject]);

  // ===============================
  // TASK ACTIONS
  // ===============================
  const createTask = async (title) => {
    if (!selectedProject) {
      toast.error("Select project first");
      return;
    }

    try {
      await api.post("/tasks", {
        title,
        description: "",
        project_id: selectedProject,
      });

      toast.success("Task created ✅");
      fetchTasks();

    } catch {
      toast.error("Create failed ❌");
    }
  };

  const updateTask = async (id, title) => {

    try {
      await api.put(`/tasks/${id}`, { title });

      // 🔥 تحديث مباشر
      setTasks(prev =>
        prev.map(task =>
          task.id === id
            ? { ...task, title }
            : task
        )
      );

      setEditingId(null);
      setEditingTitle("");

  } catch (err) {
    console.log(err);
        }
      };

  const deleteTask = async (id) => {
    await api.delete(`/tasks/${id}`);
    fetchTasks();
  };

  const toggleTask = async (task) => {
    await api.put(`/tasks/${task.id}`, {
      completed: !task.completed
    });
    fetchTasks();
  };

  // ===============================
  // FILTER
  // ===============================
  const filteredTasks = tasks.filter((t) => {
    if (filter === "active" && t.completed) return false;
    if (filter === "done" && !t.completed) return false;
    return t.title.toLowerCase().includes(search.toLowerCase());
  });

  // ===============================
  // LOADING
  // ===============================
  if (loading && selectedProject) {
    return <p>Loading...</p>;
  }

  // ===============================
  // UI
  // ===============================
  return (
    <div className="app-layout">

      <Sidebar
        tasks={tasks}
        setFilter={setFilter}
        currentFilter={filter}
      />

      <div className="container">

        <button onClick={() => {
          localStorage.removeItem("token");
          window.location.href = "/";
        }}>
          Logout
        </button>

        <h2>TaskForge ⚒️</h2>

        {/* PROJECT BAR */}
        <div style={{ display: "flex", gap: "10px" }}>

          {projects.length === 0 ? (
            <p>No projects yet 🚀</p>
          ) : (
            <select
              value={selectedProject || ""}
              onChange={(e) => setSelectedProject(Number(e.target.value))}
            >
              <option value="" disabled>Select project</option>

              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  📁 {p.name}
                </option>
              ))}
            </select>
          )}

          <button onClick={createProject}>+ New</button>

          {/* 🔥 DELETE PROJECT */}
          {selectedProject && (
            <button onClick={deleteProject}>
              🗑️
            </button>
          )}

        </div>

        {/* SEARCH */}
        <input
          ref={searchRef}
          placeholder="Search (Ctrl + K)"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {/* CREATE TASK */}
        <TaskInput createTask={createTask} />

        {/* EMPTY STATE */}
        {filteredTasks.length === 0 && selectedProject && (
          <p>No tasks yet 🚀</p>
        )}

        {/* TASK LIST */}
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