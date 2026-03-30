// =======================================
// projectService.js
// =======================================

import api from "../api/api";

// ===============================
// 📦 GET ALL PROJECTS
// ===============================
export const getProjects = async () => {
  const res = await api.get("/projects");

  // API بيرجع list مباشرة
  return res.data;
};

// ===============================
// ➕ CREATE PROJECT
// ===============================
export const createProject = async (data) => {
  const res = await api.post("/projects", data);

  return res.data;
};

// ===============================
// 🗑️ DELETE PROJECT
// ===============================
export const deleteProject = async (projectId) => {
  await api.delete(`/projects/${projectId}`);
};

// ===============================
// ✏️ (اختياري) UPDATE PROJECT
// ===============================
export const updateProject = async (projectId, data) => {
  const res = await api.put(`/projects/${projectId}`, data);

  return res.data;
};