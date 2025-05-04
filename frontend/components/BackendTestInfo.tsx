"use client";
import React, { useEffect, useState } from "react";

interface TestInfo {
  project: string;
  status: string;
  backend: string;
}

export default function BackendTestInfo() {
  const [info, setInfo] = useState<TestInfo | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    fetch("http://localhost:8000/test-info")
      .then((res) => {
        if (!res.ok) throw new Error("API error");
        return res.json();
      })
      .then(setInfo)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="text-red-500">API error: {error}</div>;
  if (!info) return <div>Loading backend info...</div>;

  return (
    <div className="bg-green-100 dark:bg-green-900 rounded p-4 my-4">
      <h3 className="font-bold mb-2">Backend Test Info</h3>
      <ul>
        <li><strong>Project:</strong> {info.project}</li>
        <li><strong>Status:</strong> {info.status}</li>
        <li><strong>Backend:</strong> {info.backend}</li>
      </ul>
    </div>
  );
}
