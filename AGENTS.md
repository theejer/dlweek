# Agent Instructions for dlweek

## Scope and Structure
- Repository root: `dlweek`
- SafePassage is an Expo-managed React Native mobile app.
- Styling direction: Tailwind utility classes through NativeWind.
- `my-app` is the active app folder and should be treated as the primary mobile app surface.
- Treat this file as the authoritative instruction source for this repository unless a deeper `AGENTS.md` is intentionally added later.

## SafePassage Operating Mode
- Default to offline-first design and degraded-mode behavior for all user-critical flows.
- Treat emergency workflows (Lost/Theft/Medical/Harassment) as high-risk UX paths: fail safe, keep steps explicit, and avoid fragile dependencies.
- For incident logs, retain data until user deletion. Keep retention transparent and user-controlled.
- Encrypt sensitive local data whenever the platform stack supports it (incident details, emergency contacts, identifiers, and precise location history).

## Command Contract
Run app commands from the active app folder (`my-app`):
- `npm start`
- `npm test`
- `npm run lint` (when available)
- `npm run typecheck` (when available)
- `npx expo-doctor`

If a script is missing from `package.json`, report and skip it. Do not invent scripts.

## Editing and Review Expectations
- Keep changes minimal and localized to the requested task.
- Include or update tests when behavior changes.
- Do not modify unrelated files.
- Prefer preserving existing project patterns unless the task requires a change.
- Prefer React Native + NativeWind patterns over web-only React patterns.
- For offline features, define behavior for both connected and disconnected states.
- Call out assumptions for GPS accuracy, cached data freshness, and map/data-pack availability.

## Skill Usage Policy
- `react-native-tailwind-builder`: default for React Native features, screens, navigation, state, and NativeWind styling.
- `security-best-practices`: mandatory by default for tasks involving emergency workflows, GPS/location, offline storage, incident logging, contacts, auth/session, and on-device AI context handling.
- `react-feature-builder`: use only for explicit legacy web maintenance tasks.
- `playwright`: use only when a browser surface exists and browser automation is explicitly needed.
- `doc`: use for structured documentation and task artifacts.

## Skill Routing Matrix
- React Native UI/feature work -> `react-native-tailwind-builder`
- Emergency or location-sensitive changes -> `react-native-tailwind-builder` + `security-best-practices`
- Data retention/storage/offline packs -> `react-native-tailwind-builder` + `security-best-practices`
- Legacy CRA web fix -> `react-feature-builder`
- Browser flow automation -> `playwright`
- Formal project docs/artifacts -> `doc`

## Output Expectations
- Always report modified files.
- Always report verification commands run and their outcomes.
- For security-sensitive tasks, report which security guidance was applied and any residual risk/tradeoff.
