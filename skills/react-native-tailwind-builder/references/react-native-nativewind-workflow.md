# React Native + NativeWind Workflow

## Assumed Stack
- React Native app with Expo-managed workflow by default.
- Tailwind-style classes implemented through NativeWind.
- JavaScript or TypeScript project layouts are both supported.

## Implementation Order
1. Identify affected screen(s), component(s), and navigation route(s).
2. Review current UI state and existing tests for the changed behavior.
3. Implement behavior changes first (state, props, handlers, data flow).
4. Apply NativeWind utility classes (`className`) for final visual structure.
5. Validate responsive behavior and platform-specific rendering.
6. Run checks and summarize outcomes.

## NativeWind Guidance
- Prefer utility classes for layout, spacing, colors, and typography.
- Consolidate repeated class sets into shared components when repetition appears.
- Keep class strings readable and grouped by purpose (layout, spacing, text, color).
- Avoid mixing many inline style objects with utility classes unless required.

## Suggested Commands
From app directory:
- `npm test -- --watchAll=false`
- `npm run lint`
- `npm run typecheck`
- `npx expo-doctor`

Run only commands that exist in the project. Missing scripts should be reported, not invented.

## Failure Handling
- Test failure: resolve assertions or implementation mismatches and rerun tests.
- Lint/type failure: fix violations and rerun checks before completion.
- Expo health failure: report actionable issues and impacted platform behavior.
- NativeWind mismatch (classes not applied): verify Babel plugin setup, content globs, and component wrappers.
