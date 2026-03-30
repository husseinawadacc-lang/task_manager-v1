import axios from "axios";

// 🔥 Create instance
const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// =============================
// 🔐 Request Interceptor (Auth)
// =============================
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// =============================
// ⚠️ Response Interceptor
// =============================
api.interceptors.response.use(
  (response) => response,

  (error) => {
    const status = error.response?.status;

    // 🔴 Unauthorized
    if (status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/";
    }

    // 🔴 Server error
    if (status >= 500) {
      console.error("Server error:", error.response);
    }

    return Promise.reject(error);
  }
);

// =============================
// 🔥 Helper Methods (اختياري)
// =============================

export const get = (url, config = {}) => api.get(url, config);
export const post = (url, data, config = {}) => api.post(url, data, config);
export const put = (url, data, config = {}) => api.put(url, data, config);
export const del = (url, config = {}) => api.delete(url, config);

// =============================

export default api;