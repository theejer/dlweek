import { env, getBackendUrlCandidates } from "@/shared/config/env";
import { getItem } from "@/features/storage/services/localStore";

const AUTH_BEARER_TOKEN_KEY = "auth_bearer_token";
const REQUEST_TIMEOUT_MS = 9500;

async function getRequestHeaders() {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = await getItem(AUTH_BEARER_TOKEN_KEY);
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs = REQUEST_TIMEOUT_MS) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function request(method: string, path: string, body?: unknown) {
  const urls = getBackendUrlCandidates();
  let lastError: unknown = null;

  for (let index = 0; index < urls.length; index += 1) {
    const baseUrl = urls[index];
    try {
      const response = await fetchWithTimeout(`${baseUrl}${path}`, {
        method,
        headers: await getRequestHeaders(),
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`API ${method} ${path} failed: ${response.status} ${text}`);
      }

      return response.status === 204 ? null : response.json();
    } catch (error) {
      lastError = error;
      const isLastCandidate = index === urls.length - 1;
      if (!isLastCandidate) {
        continue;
      }
    }
  }

  if (lastError instanceof Error) {
    if (lastError.name === "AbortError") {
      throw new Error(
        `Backend request timed out. Checked backend URLs: ${urls.join(", ")}. Ensure backend is reachable from your device.`
      );
    }
    if (lastError.message.includes("Network request failed")) {
      throw new Error(
        `Network request failed. Checked backend URLs: ${urls.join(", ")}. Ensure backend is running and reachable from your device.`
      );
    }
    throw lastError;
  }

  throw new Error(`API ${method} ${path} failed at ${env.BACKEND_URL}`);
}

export const apiClient = {
  get: (path: string) => request("GET", path),
  post: (path: string, body?: unknown) => request("POST", path, body),
  put: (path: string, body?: unknown) => request("PUT", path, body),
  patch: (path: string, body?: unknown) => request("PATCH", path, body),
  delete: (path: string) => request("DELETE", path),
};
