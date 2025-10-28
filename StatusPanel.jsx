import React, { useEffect, useState } from "react";

function StatusPanel() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/metrics");
        const json = await res.json();
        setMetrics(json);
      } catch (err) {
        console.error(err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  if (!metrics) return <p>Loading status...</p>;

  return (
    <div style={{ padding: "10px", background: "#f4f4f4", borderRadius: "8px", marginTop: "20px" }}>
      <h2>Intersection Status</h2>
      <p><b>Phase:</b> {metrics.phase}</p>
      <p><b>Time in Phase:</b> {metrics.time_in_phase}s</p>
      <p><b>Queue Lengths:</b> {metrics.queue_lengths.join(", ")}</p>
      <p><b>Wait Time:</b> {metrics.wait_time}s</p>
    </div>
  );
}

export default StatusPanel;
