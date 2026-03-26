// ===============================
// LoginPage.jsx (FINAL UPGRADED)
// ===============================

import { useState } from "react";
import api from "../api/api";
import toast from "react-hot-toast";
import {  useNavigate } from "react-router-dom";



function LoginPage() {

  // ============================
  // STATE
  // ============================

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate              =useNavigate();

  // ============================
  // HANDLE LOGIN
  // ============================

  const handleLogin = async (e) => {

    e.preventDefault();

    // ✅ validation
    if (!email || !password) {
      toast.error("Please fill all fields");
      return;
    }

    try {

      setLoading(true);

      const response = await api.post("/auth/login", {
        email,
        password
      });

      // حفظ التوكن
      localStorage.setItem("token", response.data.access_token);

      toast.success("Login successful 🎉");
      
      navigate("/dashboard");
      window.location.reload();


    } catch (error) {

      console.log("LOGIN ERROR", error);

      toast.error("Invalid email or password");

    } finally {

      setLoading(false);

    }

  };

  // ============================
  // UI
  // ============================

  return (

    <div style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      background: "#111827",
      color: "white"
    }}>

      <form
        onSubmit={handleLogin}
        style={{
          background: "#1f2937",
          padding: "30px",
          borderRadius: "12px",
          width: "300px",
          display: "flex",
          flexDirection: "column",
          gap: "15px"
        }}
      >

        <h2 style={{ textAlign: "center" }}>
          Login
        </h2>

        {/* EMAIL */}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{
            padding: "10px",
            borderRadius: "6px",
            border: "none"
          }}
        />

        {/* PASSWORD */}
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{
            padding: "10px",
            borderRadius: "6px",
            border: "none"
          }}
        />

        {/* BUTTON */}
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px",
            borderRadius: "6px",
            background: "#2563eb",
            color: "white",
            border: "none",
            cursor: "pointer"
          }}
        >

          {loading ? "Logging in..." : "Login"}

        </button>

      </form>

    </div>

  );

}

export default LoginPage;