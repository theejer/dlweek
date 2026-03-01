import { useState } from "react";
import type { UserProfile } from "@/features/user/types";
import { createUser, updateUserEmergencyContact } from "@/features/user/services/userApi";
import { setItem } from "@/features/storage/services/localStore";

const ACTIVE_USER_ID_KEY = "active_user_id";
const ACTIVE_USER_PROFILE_KEY = "active_user_profile";

// Hook orchestrates local form state + backend sync.
export function useUserProfile() {
  const [profile, setProfile] = useState<UserProfile>({ fullName: "", phone: "" });
  const [isSaving, setIsSaving] = useState(false);

  async function saveProfile() {
    setIsSaving(true);
    try {
      let resolvedUser: UserProfile = profile;

      try {
        const created = (await createUser(profile)) as UserProfile | null;
        if (created?.id && profile.emergencyContact) {
          await updateUserEmergencyContact(created.id, profile.emergencyContact);
        }
        if (created?.id) {
          resolvedUser = { ...profile, id: created.id };
        }
      } catch {
        resolvedUser = { ...profile, id: profile.id ?? `local_user_${Date.now()}` };
      }

      if (resolvedUser.id) {
        await setItem(ACTIVE_USER_ID_KEY, resolvedUser.id);
      }
      await setItem(ACTIVE_USER_PROFILE_KEY, JSON.stringify(resolvedUser));

      return resolvedUser;
    } finally {
      setIsSaving(false);
    }
  }

  return { profile, setProfile, isSaving, saveProfile };
}
