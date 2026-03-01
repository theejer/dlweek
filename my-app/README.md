# SafePassage App Workspace

This folder is the active application workspace for SafePassage.

## Purpose
- Build the Expo-managed React Native client for offline-first traveler safety.
- Implement must-have hackathon features: itinerary risk prep, emergency protocols, offline map waypoints, and phrase helper.

## Conventions
- Use NativeWind for styling.
- Keep behavior resilient when offline and explicit for emergency flows.
- Apply security review by default for location, local storage, emergency actions, and on-device AI context.

## Commands
From this directory:
- `npm start`
- `npm test`
- `npm run lint` (if script exists)
- `npm run typecheck` (if script exists)
- `npx expo-doctor`
