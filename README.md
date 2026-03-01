# SafePassage (DLW Track)

This repository hosts the SafePassage hackathon build: an offline-first safety companion for solo travelers.

## Project Direction
- Primary app surface: Expo-managed React Native in `my-app`.
- Styling: NativeWind (Tailwind utility classes).
- Priority capabilities: itinerary risk prep (online), emergency guidance (offline), offline maps, and phrase helper.

## Contributor and Agent Guidance
- Authoritative instructions live in `AGENTS.md`.
- Use `skills/react-native-tailwind-builder` for default feature work.
- Apply `skills/security-best-practices` for emergency, GPS/location, storage, and on-device AI related changes.
- Use `skills/react-feature-builder` only for explicit legacy web maintenance.

## Verification Baseline
Run commands from `my-app`:
- `npm start`
- `npm test`
- `npm run lint` (if present)
- `npm run typecheck` (if present)
- `npx expo-doctor`