"use client";

import { FormEvent, useState } from "react";

type Json = Record<string, unknown> | unknown[];

async function apiRequest(
  path: string,
  options: RequestInit,
  orgId: string
): Promise<{ status: number; data: Json | string }> {
  const res = await fetch(`/api/proxy/${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      "x-organization-id": orgId,
    },
  });

  const text = await res.text();
  try {
    return { status: res.status, data: JSON.parse(text) };
  } catch {
    return { status: res.status, data: text };
  }
}

export default function Dashboard() {
  const [orgId, setOrgId] = useState("");
  const [orgName, setOrgName] = useState("Acme Inc");
  const [jobId, setJobId] = useState("");
  const [title, setTitle] = useState("Backend Engineer");
  const [jobDescription, setJobDescription] = useState(
    "About the role\n\nWe’re hiring a Automation & Robotic Expert to join our team. "
      + "You’ll connect suppliers automation systems to internal platforms and improve operations."
  );
  const [requirements, setRequirements] = useState("");
  const [question, setQuestion] = useState("Who is strongest in Django?");
  const [sessionId, setSessionId] = useState("session-1");
  const [result, setResult] = useState<Json | string>("No response yet.");
  const resultText = typeof result === "string" ? result : JSON.stringify(result, null, 2);
  const isHtmlResult =
    typeof result === "string" &&
    (result.trimStart().toLowerCase().startsWith("<!doctype html") ||
      result.trimStart().toLowerCase().startsWith("<html"));

  const onCreateOrganization = async (e: FormEvent) => {
    e.preventDefault();
    const response = await apiRequest(
      "organizations/",
      {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ name: orgName }),
      },
      orgId
    );
    setResult(response.data);
    if (typeof response.data === "object" && response.data && "id" in response.data) {
      setOrgId(String((response.data as { id: string }).id));
    }
  };

  const onCreateJob = async (e: FormEvent) => {
    e.preventDefault();
    const response = await apiRequest(
      "jobs/",
      {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ title, job_description: jobDescription, requirements }),
      },
      orgId
    );
    setResult(response.data);
    if (typeof response.data === "object" && response.data && "id" in response.data) {
      setJobId(String((response.data as { id: string }).id));
    }
  };

  const onRankings = async (e: FormEvent) => {
    e.preventDefault();
    const response = await apiRequest(`jobs/${jobId}/rankings/`, { method: "GET" }, orgId);
    setResult(response.data);
  };

  const onChat = async (e: FormEvent) => {
    e.preventDefault();
    const response = await apiRequest(
      `jobs/${jobId}/chat/`,
      {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, question }),
      },
      orgId
    );
    setResult(response.data);
  };

  const onUpload = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const input = e.currentTarget.elements.namedItem("files") as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      setResult("Select at least one file first.");
      return;
    }
    const form = new FormData();
    Array.from(input.files).forEach((f) => form.append("files", f));

    const response = await apiRequest(
      `jobs/${jobId}/upload/`,
      { method: "POST", body: form },
      orgId
    );
    setResult(response.data);
  };

  return (
    <main>
      <h1>CV RAG Dashboard</h1>
      <p>Set your organization ID, then create jobs, upload CVs, rank candidates, and chat.</p>

      <div className="grid">
        <section className="card">
          <h2>Context</h2>
          <label>Organization Name</label>
          <input value={orgName} onChange={(e) => setOrgName(e.target.value)} placeholder="Acme Inc" />
          <form onSubmit={onCreateOrganization}>
            <button type="submit">Create Organization</button>
          </form>
          <label>Organization UUID</label>
          <input value={orgId} onChange={(e) => setOrgId(e.target.value)} placeholder="organization uuid" />
          <label>Job UUID</label>
          <input value={jobId} onChange={(e) => setJobId(e.target.value)} placeholder="job uuid" />
        </section>

        <section className="card">
          <h2>Create Job</h2>
          <form onSubmit={onCreateJob}>
            <label>Title</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} />
            <label>Job Description</label>
            <textarea rows={6} value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
            <label>Requirements</label>
            <textarea rows={4} value={requirements} onChange={(e) => setRequirements(e.target.value)} placeholder="Optional. Auto-generated from description if empty." />
            <button type="submit">Create Job</button>
          </form>
        </section>

        <section className="card">
          <h2>Upload CVs</h2>
          <form onSubmit={onUpload}>
            <input type="file" name="files" multiple accept=".pdf,.txt" />
            <button type="submit">Upload Files</button>
          </form>
        </section>

        <section className="card">
          <h2>Rankings</h2>
          <form onSubmit={onRankings}>
            <button type="submit">Fetch Rankings</button>
          </form>
        </section>

        <section className="card">
          <h2>Chat</h2>
          <form onSubmit={onChat}>
            <label>Session ID</label>
            <input value={sessionId} onChange={(e) => setSessionId(e.target.value)} />
            <label>Question</label>
            <textarea rows={3} value={question} onChange={(e) => setQuestion(e.target.value)} />
            <button type="submit">Ask</button>
          </form>
        </section>

        <section className="card">
          <h2>Response</h2>
          {isHtmlResult ? (
            <iframe className="response-frame" srcDoc={resultText} title="HTML response preview" />
          ) : (
            <pre>{resultText}</pre>
          )}
        </section>
      </div>
    </main>
  );
}
