import { NextRequest, NextResponse } from "next/server";

const backendBase = process.env.BACKEND_URL || "http://web:8000";

async function forward(req: NextRequest, path: string[]) {
  const prefix = "/api/proxy/";
  const incomingPath = req.nextUrl.pathname;
  let forwardedPath = incomingPath.startsWith(prefix)
    ? `/api/${incomingPath.slice(prefix.length)}`
    : `/api/${path.join("/")}/`;
  if (!forwardedPath.endsWith("/")) {
    forwardedPath = `${forwardedPath}/`;
  }
  const target = `${backendBase}${forwardedPath}${req.nextUrl.search}`;

  const headers = new Headers();
  const orgId = req.headers.get("x-organization-id");
  if (orgId) {
    headers.set("x-organization-id", orgId);
  }
  const contentType = req.headers.get("content-type");
  if (contentType) {
    headers.set("content-type", contentType);
  }

  const method = req.method;
  const body = method === "GET" || method === "HEAD" ? undefined : await req.arrayBuffer();

  const response = await fetch(target, {
    method,
    headers,
    body,
  });

  const output = await response.arrayBuffer();
  const nextResponse = new NextResponse(output, { status: response.status });
  const responseType = response.headers.get("content-type");
  if (responseType) {
    nextResponse.headers.set("content-type", responseType);
  }
  return nextResponse;
}

export async function GET(req: NextRequest, context: { params: { path: string[] } }) {
  return forward(req, context.params.path);
}

export async function POST(req: NextRequest, context: { params: { path: string[] } }) {
  return forward(req, context.params.path);
}

export async function PUT(req: NextRequest, context: { params: { path: string[] } }) {
  return forward(req, context.params.path);
}

export async function PATCH(req: NextRequest, context: { params: { path: string[] } }) {
  return forward(req, context.params.path);
}

export async function DELETE(req: NextRequest, context: { params: { path: string[] } }) {
  return forward(req, context.params.path);
}
