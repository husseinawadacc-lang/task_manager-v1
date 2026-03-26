import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import './index.css'
import "./styles.css";

import App from './App.jsx'
import { Toaster } from "react-hot-toast";

createRoot(document.getElementById('root')).render(
  <StrictMode>

    <>
      {/* Toast System */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#1e293b",
            color: "#e2e8f0",
            border: "1px solid #334155"
          }
        }}
      />

      {/* Main App */}
      <App />

    </>

  </StrictMode>,
)