import api from "../api/api"

// 🔥 تحليل task
export const analyzeTask = async (text) => {
  const res = await api.post("/ai/analyze-task", { text :text })
  return res.data
}

// 🔥 توليد subtasks
export const generateSubtasks = async (title) => {
  const res = await api.post("/ai/suggest-subtasks", { title :title })
  return res.data.subtasks
}

// 🔥 إنشاء task من AI
export const createTaskFromAI = async (text, projectId) => {
  const res = await api.post(
    `/ai/create-task-from-ai?project_id=${projectId}`,
    { text }
  )
  return res.data
}