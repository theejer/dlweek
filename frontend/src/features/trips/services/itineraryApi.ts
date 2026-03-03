import { apiClient } from "@/lib/apiClient";
import NetInfo from "@react-native-community/netinfo";
import type { Day } from "@/features/trips/types";
import {
  enqueueSyncJob,
  getItinerary,
  initializeOfflineDb,
  type SyncQueueJob,
  upsertItinerary as upsertLocalItinerary,
} from "@/features/storage/services/offlineDb";
import { canSyncItineraryOnline } from "@/shared/utils/syncGuards";

type DayWire = {
  date: string;
  locations: Array<{
    name: string;
    district?: string;
    block?: string;
    connectivity_zone?: string;
    assumed_location_risk?: string;
  }>;
  accommodation?: string;
};

type DayWireFlexible = {
  date?: string;
  day_label?: string;
  accommodation?: string;
  stay?: string;
  hotel?: string;
  locations?: Array<{
    name?: string;
    location?: string;
    place?: string;
    activity?: string;
    district?: string;
    block?: string;
    connectivity_zone?: string;
    connectivityZone?: string;
  }>;
};

type ItineraryResponseWire = {
  days?: DayWireFlexible[];
  itinerary_json?: {
    days?: DayWireFlexible[];
  };
  itinerary?: {
    days?: DayWireFlexible[];
  };
};

const UPLOAD_TIMEOUT_MS = 40000;

async function fetchWithTimeout(url: string, init: RequestInit, timeoutMs = UPLOAD_TIMEOUT_MS) {
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

function toWireDays(days: Day[]): DayWire[] {
  return days.map((day) => ({
    date: day.date,
    accommodation: day.accommodation,
    locations: day.locations.map((location) => ({
      name: location.name,
      district: location.district,
      block: location.block,
      connectivity_zone: location.connectivityZone,
    })),
  }));
}

function fromWireDays(days: DayWireFlexible[]): Day[] {
  return days.map((day) => ({
    date: day.date ?? day.day_label ?? "",
    accommodation: day.accommodation ?? day.stay ?? day.hotel,
    locations: (day.locations ?? [])
      .map((location) => {
        const locationName = location.name ?? location.location ?? location.place ?? location.activity ?? "";
        return {
          name: locationName,
          district: location.district,
          block: location.block,
          connectivityZone: (location.connectivity_zone ?? location.connectivityZone) as Day["locations"][number]["connectivityZone"],
        };
      })
      .filter((location) => location.name.trim().length > 0),
  }));
}

function extractDaysFromItineraryResponse(response: ItineraryResponseWire, fallback: DayWireFlexible[] = []): Day[] {
  const candidateDays = Array.isArray(response.days)
    ? response.days
    : Array.isArray(response.itinerary_json?.days)
    ? response.itinerary_json?.days
    : Array.isArray(response.itinerary?.days)
    ? response.itinerary?.days
    : fallback;

  return fromWireDays(candidateDays ?? []);
}

async function isDeviceOffline() {
  try {
    const net = await NetInfo.fetch();
    const connected = Boolean(net.isConnected) && Boolean(net.isInternetReachable ?? true);
    return !connected;
  } catch {
    return false;
  }
}

// Routes itinerary JSON to backend and fetches latest snapshot.
export async function upsertItinerary(tripId: string, days: Day[]) {
  await initializeOfflineDb();

  const wireDays = toWireDays(days);

  // Always write to SQLite first
  await upsertLocalItinerary(tripId, days);

  // Then attempt to sync remotely
  if (canSyncItineraryOnline(tripId)) {
    try {
      const response = (await apiClient.put(`/trips/${tripId}/itinerary`, { days: wireDays, meta: {} })) as ItineraryResponseWire;
      // Update with server response if successful
      const normalizedDays = extractDaysFromItineraryResponse(response, wireDays);
      await upsertLocalItinerary(tripId, normalizedDays);
      return response;
    } catch {
      // If remote sync fails, queue for retry
      await enqueueSyncJob({
        entityType: "itinerary",
        entityId: tripId,
        operation: "upsert",
        payload: { trip_id: tripId, days: wireDays, meta: {} },
      });
      return { trip_id: tripId, days: wireDays, meta: { saved: false, local_only: true } };
    }
  } else {
    // No trip context or offline; queue for later
    await enqueueSyncJob({
      entityType: "itinerary",
      entityId: tripId,
      operation: "upsert",
      payload: { trip_id: tripId, days: wireDays, meta: {} },
    });
    return { trip_id: tripId, days: wireDays, meta: { saved: false, local_only: true } };
  }
}

export async function getLatestItinerary(tripId: string) {
  await initializeOfflineDb();

  if (!canSyncItineraryOnline(tripId)) {
    return getItinerary(tripId);
  }

  try {
    const response = (await apiClient.get(`/trips/${tripId}/itinerary`)) as ItineraryResponseWire;
    const normalizedDays = extractDaysFromItineraryResponse(response, []);
    if (normalizedDays.length > 0) {
      await upsertLocalItinerary(tripId, normalizedDays);
      return normalizedDays;
    }
    return getItinerary(tripId);
  } catch {
    return getItinerary(tripId);
  }
}

// Upload itinerary document and extract structured itinerary.
export async function uploadItineraryPDF(formData: FormData) {
  const { env, getBackendUrlCandidates } = await import("@/shared/config/env");
  const urls = getBackendUrlCandidates();
  let lastError: unknown = null;

  for (let index = 0; index < urls.length; index += 1) {
    const baseUrl = urls[index];
    try {
      const response = await fetchWithTimeout(`${baseUrl}/trips/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Failed to upload itinerary file: ${response.status} ${error}`);
      }

      const result = (await response.json()) as { days?: DayWireFlexible[] };
      return fromWireDays(result.days ?? []);
    } catch (error) {
      lastError = error;
      const isLastCandidate = index === urls.length - 1;
      if (!isLastCandidate) {
        continue;
      }
    }
  }

  if (lastError instanceof Error && lastError.message.includes("Network request failed")) {
    throw new Error(
      `Network request failed while uploading itinerary. Checked backend URLs: ${urls.join(", ")}. Ensure backend is running and reachable from your phone.`
    );
  }

  if (lastError instanceof Error && lastError.name === "AbortError") {
    throw new Error(
      `Upload request timed out. Checked backend URLs: ${urls.join(", ")}. Ensure backend is reachable from your phone.`
    );
  }

  if (lastError instanceof Error) {
    throw lastError;
  }

  throw new Error(`Failed to upload itinerary file at ${env.BACKEND_URL}`);
}

export async function replayItinerarySyncJob(job: SyncQueueJob) {
  if (job.entity_type !== "itinerary") {
    throw new Error(`unsupported sync job entity type: ${job.entity_type}`);
  }

  const payload = JSON.parse(job.payload_json) as { trip_id?: string; days?: DayWire[]; meta?: Record<string, unknown> };
  const tripId = String(payload.trip_id ?? job.entity_id);
  const response = (await apiClient.put(`/trips/${tripId}/itinerary`, {
    days: payload.days ?? [],
    meta: payload.meta ?? {},
  })) as ItineraryResponseWire;

  const normalizedDays = extractDaysFromItineraryResponse(response, payload.days ?? []);
  await upsertLocalItinerary(tripId, normalizedDays);
}
