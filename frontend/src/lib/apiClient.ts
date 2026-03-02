import { env, getBackendUrlCandidates } from "@/shared/config/env";
import { getItem } from "@/features/storage/services/localStore";

const AUTH_BEARER_TOKEN_KEY = "auth_bearer_token";

async function getRequestHeaders() {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = await getItem(AUTH_BEARER_TOKEN_KEY);
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function request(method: string, path: string, body?: unknown) {
  const urls = getBackendUrlCandidates();
  let lastError: unknown = null;

  for (let index = 0; index < urls.length; index += 1) {
    const baseUrl = urls[index];
    try {
      const response = await fetch(`${baseUrl}${path}`, {
        method,
        headers: await getRequestHeaders(),
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`API ${method} ${path} failed: ${response.status} ${text}`);
      }

  return response.status === 204 ? null : response.json();
}

export const apiClient = {
  get: (path: string) => request("GET", path),
  post: (path: string, body?: unknown) => request("POST", path, body),
  put: (path: string, body?: unknown) => request("PUT", path, body),
  patch: (path: string, body?: unknown) => request("PATCH", path, body),
};
