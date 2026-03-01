# JavaScript/TypeScript React Native Mobile Security Best Practices

Use this guidance for React Native applications, especially offline-first and safety-critical workflows.

## 1) Threat Model Baseline
- Assume device compromise is possible (lost/stolen device, malware, rooted/jailbroken environments).
- Assume intermittent connectivity and delayed server synchronization.
- Distinguish between data that is safe to cache and data that must be protected at rest.
- In safety-critical flows, prefer deterministic fallback behavior over dynamic/network-dependent logic.

## 2) Data Classification and Storage
Classify local data before implementation:
- **Highly sensitive:** incident logs with photos/notes, precise location history, personal identifiers, emergency contacts.
- **Sensitive:** itinerary details, risk scoring history, phone numbers, call intents.
- **Low sensitivity:** static phrase packs, public map tiles, static protocol templates.

Storage requirements:
- Use platform secure storage (iOS Keychain / Android Keystore-backed solutions) for secrets/tokens/keys.
- Encrypt highly sensitive local records where practical.
- Avoid storing long-lived auth tokens in plain AsyncStorage.
- Define explicit retention behavior; if user-managed deletion is required, provide clear delete/export controls.

## 3) Permission and Privacy Controls
- Request location, microphone, and media permissions only when needed and with clear purpose text.
- Follow least-privilege access; do not pre-request broad permissions at app launch.
- Provide a clear privacy explanation for what data stays on-device vs syncs to cloud.
- Avoid hidden background tracking; collect location only when necessary for active flow.

## 4) Network and API Security
- Use HTTPS/TLS for all API communications.
- Validate server responses and guard against malformed/unexpected payloads.
- Do not trust client-side risk scores or flags for authorization decisions.
- Ensure offline queue replay is idempotent and authenticated when connectivity returns.

## 5) Emergency Workflow Safety
- Emergency UX must be resilient when data is stale/missing.
- Never block emergency protocol rendering on non-critical dependencies.
- Prefer static, validated protocol steps when model output is unavailable.
- Protect against accidental emergency triggers (confirmation steps for irreversible actions).

## 6) On-Device AI and Prompt Safety
- Minimize sensitive context passed to model prompts.
- Never include secrets, auth material, or unnecessary identifiers in prompts.
- Apply output constraints for emergency instructions (no unsafe medical/legal claims, no fabricated contacts).
- Log model failures safely without exposing sensitive prompt context.

## 7) Logging and Telemetry
- Redact PII and sensitive location data from logs by default.
- Avoid debug logging of full payloads in production.
- Use structured error categories that preserve diagnostics without leaking user data.

## 8) Validation Checklist
Before shipping mobile changes, confirm:
- Sensitive storage paths are encrypted/secure.
- Permission prompts are contextual and minimal.
- Offline fallback behavior is deterministic and tested.
- Emergency actions remain usable without internet.
- Security-sensitive assumptions are documented.
