# React CRA Workflow Reference

## Scope
Use this workflow for feature requests, UI updates, and bug fixes in Create React App style projects.

## Execution Order
1. Identify affected files in `src/` and the related test files.
2. Confirm current behavior from component code and tests.
3. Apply minimal code changes for the requested behavior.
4. Update or add tests when behavior changes.
5. Run verification checks in order:
   - targeted test command (if relevant)
   - full test run
   - production build
6. Report changed files and command results.

## Practical Guidance
- Prefer functionally local edits over architecture changes.
- Keep UI and test updates in the same task when behavior changes.
- Reuse existing patterns for state handling, naming, and styling.
- If requirements are ambiguous, choose the safest minimal implementation and state assumptions.

## Suggested Commands
From app directory (`my-app`):
- `npm test -- --watchAll=false`
- `npm test -- --watchAll=false <test-file-pattern>`
- `npm run build`

## Failure Handling
- If tests fail, inspect the failing assertion and update implementation or tests accordingly.
- If build fails, resolve compile/lint issues and rerun build before completion.
- If command tooling is missing, report the missing dependency and provide the exact failing command.
