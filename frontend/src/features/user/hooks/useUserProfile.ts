import { useState } from "react";
import type { UserProfile } from "@/features/user/types";
import { createUser, updateUserEmergencyContact } from "@/features/user/services/userApi";

// Hook orchestrates local form state + backend sync.
export function useUserProfile() {
  const [profile, setProfile] = useState<UserProfile>({ fullName: "", phone: "" });
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function saveProfile() {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const created = await createUser(profile);
      if (created?.id && profile.emergencyContact) {
        await updateUserEmergencyContact(created.id, profile.emergencyContact);
      }
      setSuccess(true);
      return created;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to save profile";
      setError(message);
      throw err;
    } finally {
      setIsSaving(false);
    }
  }

  return { profile, setProfile, isSaving, saveProfile, error, success };
}
