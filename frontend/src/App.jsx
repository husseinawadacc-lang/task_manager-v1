// ===============================
// App.jsx (FINAL VERSION)
// ===============================

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";
import Landing from "./pages/Landing";

function App() {

  const token = localStorage.getItem("token");

  return (
    <BrowserRouter>

      <Routes>

        {/* ===============================
            LANDING (PUBLIC)
        =============================== */}
        <Route path="/" element={<Landing />} />

        {/* ===============================
            LOGIN
        =============================== */}
        <Route
          path="/login"
          element={
            !token ? (
              <LoginPage />
            ) : (
              <Navigate to="/dashboard" />
            )
          }
        />

        {/* ===============================
            DASHBOARD (PROTECTED)
        =============================== */}
        <Route
          path="/dashboard"
          element={
            token ? (
              <Dashboard />
            ) : (
              <Navigate to="/login" />
            )
          }
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;