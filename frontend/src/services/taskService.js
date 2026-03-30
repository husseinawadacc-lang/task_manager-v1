import api from "../api/api"

// 📌 إنشاء task
export const createTask = async (data) => {
  const res = await api.post("/tasks", data)
  return res.data
}

// 📌 جلب task واحد
export const getTask = async (taskId) => {
  const res = await api.get(`/tasks/${taskId}`)
  return res.data
}

// 📌 جلب كل tasks
export const getTasks = async (projectId) => {
  const res = await api.get("/tasks", {
    params: { project_id: projectId },
  })
  return res.data
}

// 📌 تحديث task
export const updateTask = async (taskId, data) => {
  const res = await api.put(`/tasks/${taskId}`, data)
  return res.data
}

// 📌 حذف task
export const deleteTask = async (taskId) => {
  await api.delete(`/tasks/${taskId}`)
}