/**
 * BackendTestInfo.tsx
 *
 * Displays backend connection and status info for development/debugging.
 * Fetches data from /test-info endpoint and shows status or error.
 *
 * Exports:
 *   - BackendTestInfo: React.FC for backend info display.
 */
"use client";
import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { Terminal, Loader2 } from "lucide-react"; // Loader2 for a spinning animation

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
        if (!res.ok) {
          // Try to parse error from backend if available
          return res
            .json()
            .then((errData) => {
              throw new Error(errData.detail || "API request failed");
            })
            .catch(() => {
              throw new Error(`API request failed with status: ${res.status}`);
            });
        }
        return res.json();
      })
      .then(setInfo)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <Alert variant="destructive" className="my-4">
        <Terminal className="h-4 w-4" />
        <AlertTitle>API Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!info) {
    return (
      <div className="flex items-center justify-center my-4 p-4 rounded-md border">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
        Loading backend info...
      </div>
    );
  }

  return (
    <Card className="my-4">
      <CardHeader>
        <CardTitle className="text-lg">Backend Test Info</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-1 text-sm">
          <li>
            <strong>Project:</strong> {info.project}
          </li>
          <li>
            <strong>Status:</strong> {info.status}
          </li>
          <li>
            <strong>Backend:</strong> {info.backend}
          </li>
        </ul>
      </CardContent>
    </Card>
  );
}
