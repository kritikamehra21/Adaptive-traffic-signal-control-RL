import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

function TrafficChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/metrics");
        const json = await res.json();
        setData((prev) => [
          ...prev.slice(-20), // keep last 20 points
          { step: json.step, wait: json.wait_time }
        ]);
      } catch (err) {
        console.error(err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ marginTop: "20px" }}>
      <h2>Average Wait Time (live)</h2>
      <LineChart width={600} height={300} data={data}>
        <XAxis dataKey="step" />
        <YAxis />
        <CartesianGrid stroke="#ccc" />
        <Tooltip />
        <Line type="monotone" dataKey="wait" stroke="#8884d8" />
      </LineChart>
    </div>
  );
}

export default TrafficChart;
