# React Native + NativeWind Workflow

## Assumed Stack
- React Native app with Expo-managed workflow by default.
- Tailwind-style classes implemented through NativeWind.
- JavaScript or TypeScript project layouts are both supported.
- SafePassage flows are offline-first and include security-sensitive emergency scenarios.

## Implementation Order
1. Identify affected screen(s), component(s), and navigation route(s).
2. Review current UI state and existing tests for the changed behavior.
3. Define behavior in both connected and offline modes before coding.
4. Implement behavior changes first (state, props, handlers, data flow).
5. Apply NativeWind utility classes (`className`) for final visual structure.
6. Validate responsive behavior and platform-specific rendering.
7. For emergency/location/storage/model-context changes, include security best-practice checks.
8. Run checks and summarize outcomes.

## NativeWind Guidance
- Prefer utility classes for layout, spacing, colors, and typography.
- Consolidate repeated class sets into shared components when repetition appears.
- Keep class strings readable and grouped by purpose (layout, spacing, text, color).
- Avoid mixing many inline style objects with utility classes unless required.
- Keep emergency-state screens visually unambiguous (high contrast, obvious action hierarchy).

## Suggested Commands
From app directory:
- `npm test -- --watchAll=false`
- `npm run lint`
- `npm run typecheck`
- `npx expo-doctor` (Expo projects)

Run only commands that exist in the project. Missing scripts should be reported, not invented.

## Failure Handling
- Test failure: resolve assertions or implementation mismatches and rerun tests.
- Lint/type failure: fix violations and rerun checks before completion.
- Expo health failure: report actionable issues and impacted platform behavior.
- NativeWind mismatch (classes not applied): verify Babel plugin setup, content globs, and component wrappers.
- Offline data missing or stale: define and document fallback behavior before completion.
