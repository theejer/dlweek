---
name: react-native-tailwind-builder
description: Build and verify React Native features styled with Tailwind utility classes through NativeWind. Use when tasks involve React Native screens/components, navigation flows, mobile bug fixes, NativeWind class updates, or validation of mobile app behavior with tests and build checks.
---

# React Native Tailwind Builder

Implement mobile feature work in a strict, low-regression workflow for React Native projects using Tailwind-style utility classes via NativeWind.

## Workflow
1. Inspect impacted screens/components, navigation paths, and related tests.
2. Confirm current behavior before edits, including style behavior on different screen sizes.
3. Implement the smallest React Native change that satisfies the request.
4. Apply or adjust NativeWind utility classes for styling updates.
5. Run verification checks (tests, lint/type checks, and build health checks when available).
6. Summarize modified files, assumptions, and command outcomes.

## Constraints
- Avoid broad refactors unless explicitly requested.
- Preserve existing project conventions and folder structure.
- Prefer reusable UI primitives and shared style tokens when available.
- Document assumptions before risky changes, especially around navigation and platform behavior.
- Do not change unrelated files.

## Styling Rules
- Use NativeWind utility classes via `className` for styling.
- Prefer shared utility patterns and design tokens over one-off inline styles.
- Use `StyleSheet` only when utility classes are insufficient (for dynamic or platform-specific cases).
- Keep spacing/typography scales consistent across screens.

## Verification
- Use `scripts/run-rn-checks.ps1` for deterministic non-interactive checks.
- Run with `-WhatIf` to preview commands.
- When scripts are missing in `package.json`, the checker reports and skips them.

## References
- Read `references/react-native-nativewind-workflow.md` for setup assumptions, implementation order, and failure handling.
