// ===============================
// TaskForge Landing (PRO UI)
// ===============================

import { useNavigate } from "react-router-dom";

function Landing() {

  const navigate = useNavigate();

  return (
    <div style={{
      fontFamily: "sans-serif",
      background: "#0f172a",
      color: "white",
      minHeight: "100vh"
    }}>

      {/* ================= NAVBAR ================= */}
      <nav style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "20px 40px"
      }}>
        <h2>TaskForge ⚒️</h2>

        <button
          onClick={() => navigate("/login")}
          style={{
            background: "#22c55e",
            border: "none",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: "pointer"
          }}
        >
          Login
        </button>
      </nav>

      {/* ================= HERO ================= */}
      <section style={{
        textAlign: "center",
        padding: "100px 20px"
      }}>

        <h1 style={{
          fontSize: "48px",
          marginBottom: "20px"
        }}>
          Build Your Productivity System ⚡
        </h1>

        <p style={{
          fontSize: "18px",
          opacity: 0.7,
          maxWidth: "600px",
          margin: "0 auto"
        }}>
          Organize tasks, manage projects, and boost your focus with TaskForge.
        </p>

        <button
          onClick={() => navigate("/login")}
          style={{
            marginTop: "30px",
            padding: "14px 28px",
            fontSize: "16px",
            background: "#22c55e",
            border: "none",
            borderRadius: "10px",
            cursor: "pointer"
          }}
        >
          Start for Free 🚀
        </button>
      </section>

      {/* ================= FEATURES ================= */}
      <section style={{
        padding: "60px 20px",
        background: "#111827"
      }}>

        <h2 style={{ textAlign: "center", marginBottom: "40px" }}>
          Features
        </h2>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "20px"
        }}>

          <div style={{ background: "#1f2937", padding: "20px", borderRadius: "10px" }}>
            <h3>📁 Multi Projects</h3>
            <p>Organize tasks across multiple projects easily.</p>
          </div>

          <div style={{ background: "#1f2937", padding: "20px", borderRadius: "10px" }}>
            <h3>⚡ Fast UI</h3>
            <p>Clean and responsive interface for speed.</p>
          </div>

          <div style={{ background: "#1f2937", padding: "20px", borderRadius: "10px" }}>
            <h3>🤖 Smart Priority</h3>
            <p>AI helps you focus on what matters.</p>
          </div>

          <div style={{ background: "#1f2937", padding: "20px", borderRadius: "10px" }}>
            <h3>🔒 Secure</h3>
            <p>Your data is isolated and protected.</p>
          </div>

        </div>
      </section>

      {/* ================= CTA ================= */}
      <section style={{
        textAlign: "center",
        padding: "80px 20px"
      }}>
        <h2>Ready to boost your productivity?</h2>

        <button
          onClick={() => navigate("/login")}
          style={{
            marginTop: "20px",
            padding: "14px 28px",
            fontSize: "16px",
            background: "#22c55e",
            border: "none",
            borderRadius: "10px",
            cursor: "pointer"
          }}
        >
          Get Started 🚀
        </button>
      </section>

      {/* ================= FOOTER ================= */}
      <footer style={{
        textAlign: "center",
        padding: "20px",
        opacity: 0.5
      }}>
        © 2026 TaskForge
      </footer>

    </div>
  );
}

export default Landing;