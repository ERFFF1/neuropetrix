"use client";
import { useEffect, useState } from "react";
export default function Home() {
  const [ping, setPing] = useState("...");
  useEffect(() => {
    fetch("/api-proxy/healthz")
      .then(r => r.json())
      .then(j => setPing(JSON.stringify(j)))
      .catch(() => setPing("API erişilemedi"));
  }, []);
  async function runJob() {
    const res = await fetch("/api-proxy/api/v1/analysis/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ case_id: "demo-001", tasks: ["radiomics"], options: {} })
    });
    const j = await res.json();
    alert(`Job accepted: ${j.job_id}`);
  }
  return (
    <main style={{ padding: 24 }}>
      <h1>NeuroPETRIX Web Bridge</h1>
      <p>API ping: {ping}</p>
      <button onClick={runJob} style={{ padding: 12, borderRadius: 8, background: "#4f46e5", color: "white" }}>
        Run Analysis
      </button>
    </main>
  );
}
