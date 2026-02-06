# OpenClaw Integration: Chimera Availability & Discovery

## Purpose
Describe how Chimera announces its availability and status to the OpenClaw network, the canonical fields published, and how peer agents discover or subscribe to those updates.

## The Sovereignty Broadcast Strategy
Project Chimera interacts with the OpenClaw network as a Sovereign Node. To maintain a reliable presence, Chimera publishes identity and status information in a versioned, signed form so peers can discover, validate, and optionally subscribe to updates.

## Published Fields (availability / status)
Chimera's status broadcasts are deliberately small and signed. Every availability announcement SHOULD include the following canonical fields:

- `agent_id` (string): Chimera's canonical decentralized identifier (DID, UUID, or other agreed agent ID). This is the primary key used in manifests and topics.
- `status` (string): One of {`available`, `negotiating`, `busy`, `maintenance`, `offline`} that represents engagement state.
- `last_ingestion_timestamp` (string, ISO8601): Timestamp of the most recent ingestion event processed by this agent.

Optional supporting fields (MAY be included):

- `capacity_score` (number): 0–100 relative score indicating ability to accept new work.
- `supported_domains` (array[string]): domain tags surfaced in the A2A manifest.
- `sequence` (integer): monotonic counter for each broadcast to detect missed updates.
- `signature` (string): cryptographic signature (base64) covering the payload for verification.

Example status payload (JSON):

```json
{
  "agent_id": "did:chimera:1234abcd",
  "status": "available",
  "last_ingestion_timestamp": "2026-02-06T14:22:03Z",
  "capacity_score": 78,
  "sequence": 4521,
  "signature": "<base64-sig>"
}
```

## Where Chimera publishes
- A2A Manifest: the long-lived manifest (versioned JSON) advertises `agent_id`, supported interfaces, and preferred discovery endpoints/topics.
- Gossip / Pub-Sub: short-lived heartbeats and status updates are published to a network topic derived from `agent_id` (e.g., `openclaw/status/<agent_id>`).
- Discovery index / Registry: optional pull endpoint where peers can fetch the last-known signed status and manifest.
- Webhooks / Push: optional push subscriptions listed in the manifest for authorized consumers.

## Discovery & Subscription Patterns
- Manifest-first discovery: peers locate Chimera by fetching the A2A manifest (e.g., from a registry or DHT entry). The manifest contains the `agent_id` and preferred topic/endpoints for status.
- Subscribe to status topic: peers subscribe to Chimera's pub/sub/gossip topic to receive real-time heartbeats.
- Pull-on-demand: when initiating negotiation, a peer may pull the latest signed status from the registry to avoid relying on cached messages.
- Push subscriptions: authorized peers can register a webhook (per manifest) to receive push notifications on state transitions.

## Validation & Security
- All status payloads MUST be signed by Chimera's active key pair. Consumers MUST verify the signature before trusting the payload.
- Use short TTLs for status messages (example: 30–120s) so subscribers avoid acting on stale information.
- The Judge Agent and HITL approval flags are authoritative for transitions into `negotiating` or `executing` states; subscribers should treat those fields with higher trust weight.
- Peers MUST validate the `sequence` or `timestamp` to detect missed or out-of-order messages; reconciliation may be performed by fetching the manifest/registry entry.

## Operational guidance
- Keep status broadcasts minimal; include `last_ingestion_timestamp` so consumers know recency of data availability.
- Publish `capacity_score` when internal scheduling is used to help the swarm make load-aware decisions.
- Log broadcasts to on-chain proofs or audit logs when required by governance policies.

## Discovery Example flow
1. Peer queries the discovery registry for agents matching `supported_domains`.
2. Peer fetches Chimera's A2A manifest and learns the status topic: `openclaw/status/did:chimera:1234abcd`.
3. Peer subscribes to the topic or pulls the current signed status from the registry.
4. When the peer detects `status: available`, it verifies signature and optionally initiates a Trust Verification handshake before negotiating.

## Traceability
- Map each published field to a requirement or acceptance criterion in feature specs (e.g., `last_ingestion_timestamp` → data-model ingestion traceability requirement).

---
Generated/updated to include canonical `agent_id`, `status`, and `last_ingestion_timestamp` fields and subscription patterns.
