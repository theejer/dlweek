import Constants from "expo-constants";
import { Platform } from "react-native";

const DEFAULT_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL ?? "http://localhost:5000";

function extractHost(raw: string | null | undefined) {
  if (!raw) return null;

  const normalized = raw.replace(/^https?:\/\//, "").split("/")[0]?.trim();
  if (!normalized) return null;

  const host = normalized.split(":")[0]?.trim();
  if (!host || host === "localhost" || host === "127.0.0.1" || host === "0.0.0.0") {
    return null;
  }

  return host;
}

function parseDevHostUrl() {
  const constantsAny = Constants as unknown as {
    expoGoConfig?: { debuggerHost?: string };
    manifest2?: { extra?: { expoClient?: { hostUri?: string } } };
    manifest?: { debuggerHost?: string };
    expoConfig?: { hostUri?: string };
  };

  const candidateHostUris = [
    constantsAny.expoConfig?.hostUri,
    constantsAny.expoGoConfig?.debuggerHost,
    constantsAny.manifest2?.extra?.expoClient?.hostUri,
    constantsAny.manifest?.debuggerHost,
  ];

  for (const uri of candidateHostUris) {
    const host = extractHost(uri);
    if (host) {
      return `http://${host}:5000`;
    }
  }

  return null;
}

export function isLocalhostUrl(url: string) {
  return (
    url.includes("localhost") ||
    url.includes("127.0.0.1") ||
    url.includes("0.0.0.0")
  );
}

export function getBackendUrlCandidates() {
  const candidates = [DEFAULT_BACKEND_URL];

  if (isLocalhostUrl(DEFAULT_BACKEND_URL)) {
    const devHostUrl = parseDevHostUrl();
    if (Platform.OS !== "web") {
      if (devHostUrl) {
        candidates.unshift(devHostUrl);
      }

      candidates.push(DEFAULT_BACKEND_URL.replace("localhost", "10.0.2.2"));
      candidates.push(DEFAULT_BACKEND_URL.replace("127.0.0.1", "10.0.2.2"));
    } else if (devHostUrl) {
      candidates.push(devHostUrl);
    }
  }

  return Array.from(new Set(candidates));
}

// Centralized environment access for runtime configuration.
export const env = {
  BACKEND_URL: DEFAULT_BACKEND_URL,
  FEATURE_OFFLINE_LLM: (process.env.EXPO_PUBLIC_FEATURE_OFFLINE_LLM ?? "false") === "true",
};
