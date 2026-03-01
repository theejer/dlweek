# Agent Instructions for dlweek

## Scope and Structure
- Repository root: `dlweek`
- Target application direction: React Native mobile app.
- Styling direction: Tailwind utility classes through NativeWind.
- Existing `my-app` may be transitional web starter code; prioritize mobile architecture decisions for new work.
- Treat this file as the authoritative instruction source for this repository unless a deeper `AGENTS.md` is intentionally added later.

## Command Contract
Run app commands from the active app folder (default: `my-app` until renamed):
- `npm start` (or Expo start command)
- `npm test`
- `npm run lint` (when available)
- `npm run typecheck` (when available)
- `npx expo-doctor` (for Expo-based mobile health checks)

## Editing and Review Expectations
- Keep changes minimal and localized to the requested task.
- Include or update tests when behavior changes.
- Do not modify unrelated files.
- Prefer preserving existing project patterns unless the task requires a change.
- Prefer React Native + NativeWind patterns over web-only React patterns.

## Skill Usage Policy
- Use `react-native-tailwind-builder` for React Native feature and styling work.
- Use `react-feature-builder` only for legacy web-specific tasks.
- Use `playwright` only when a browser-based surface exists and requires E2E checks.
- Use `security-best-practices` for security-sensitive changes.
- Use `doc` for structured documentation and task artifacts.

## Output Expectations
- Always report modified files.
- Always report verification commands run and their outcomes.
