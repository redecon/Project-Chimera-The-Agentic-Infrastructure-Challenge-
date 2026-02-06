# Security Specification — Project Chimera

Purpose

Define a precise, end-to-end security spec for Project Chimera covering authentication/authorization, secrets management, rate limiting, content safety, agent containment, and CI/CD governance integration. The spec is actionable and prescriptive so an autonomous agent can implement controls, CI checks, and runtime enforcement.

## 1. Authentication & Authorization

### Strategy
- Authentication: OAuth2 Authorization Code flow for user-facing UI and Client Credentials flow for service-to-service. Use JWT access tokens (RS256 signed) with short lifetimes (default `access_token`=5m, `refresh_token`=1h). Public keys must be published via a JWKS endpoint hosted by the auth service.
- Authorization: Role-Based Access Control (RBAC) with resource scoping. Roles:
  - `operator` — can create campaigns, view dashboards, export analytics.
  - `moderator` — can view ContentReviewPage, resolve escalations, view provenance, not allowed to modify system settings.
  - `developer` — can view logs, change integrations in `Settings`, trigger CI jobs; limited access to production-only actions.
  - `service` — machine identity used by backend services (client credentials).
- Token claims MUST include `sub`, `roles` (array), `iss`, `aud`, `exp`, `iat`, and `jti`.
- Authorization checks:
  - All API endpoints MUST check `Authorization: Bearer <token>` and validate signature, `exp`, `aud`, and `iss`.
  - Implement fine-grained permission checks via Ability/Policy layer (e.g., `can_publish(enriched_trend_id, user)`), not via role-only checks.

### Implementation Notes
- Integrate an identity provider (IdP) such as Auth0/Keycloak or enterprise SSO. Services use Client Credentials and rotate client secrets regularly.
- Admin actions (e.g., alter HITL thresholds) MUST require `operator`+`developer` roles or an explicit `admin` grant and require MFA in the UI.

## 2. Secrets Management

### Vaulting
- Use enterprise-grade vault: prefer HashiCorp Vault or AWS Secrets Manager. Do not store secrets in repo or environment files. Secrets include: API keys (Coinbase, social APIs), DB credentials, JWT private keys, third-party integration tokens.
- Access pattern:
  - At runtime, services request secrets from Vault using machine identity (e.g., AWS IAM role or Vault AppRole). Tokens are short-lived and cached in-memory with automatic rotation.
  - For local dev, use `vault dev` or a dev-secrets shim; CI uses ephemeral secrets injected only into runner environment variables.

### Environment Variables
- Allowed env vars: only non-sensitive config (feature flags, endpoints). Sensitive keys must reference Vault paths and NOT be present in plaintext. Example:

```
DATABASE_URL=postgresql://{{vault:secret/path#DB_URI}}
WEAVIATE_URL=https://weaviate.example
COINBASE_API_KEY={{vault:secret/payments#COINBASE_KEY}}
```

- CI: use platform secret stores for injecting env vars at runtime; rotate and revoke if leakage suspected.

### Secret usage policies
- All secrets access MUST be logged with `who`, `when`, `what` (read/write) and stored in audit logs in Vault.
- Prohibit printing secrets in logs or returning them in APIs. CI jobs must scan logs for secret patterns and fail if detected.

## 3. Rate Limiting & Throttling

### Per-endpoint limits (default)
- `POST /publish`: max 100 requests per minute per `operator` account (burst 20). Excess → `429 Too Many Requests` with `Retry-After` header.
- `POST /ingest`: max 500 requests per minute per source (API key). For unauthenticated client sources, apply global lower cap 60 rpm.
- `GET /trends`, `GET /analytics`: max 1000 requests per minute per service account.
- `POST /escalations/{id}/resolve`: max 60 requests per minute per moderator.

### Global throttling
- System-wide cap: if total publish requests exceed `PUBLISH_GLOBAL_RATE_LIMIT` (default 2000 rpm), enter throttled mode: new publish requests return `503 Service Unavailable` with `Retry-After` and an alert triggers.
- Implement leaky-bucket or token-bucket algorithm at API gateway (NGINX, Envoy) and at application logic as fallback.

### Enforcement & Monitoring
- Rate limits enforced at API gateway with per-API-key and per-IP keys; fallback enforcement in application layer to prevent circumvention.
- Emit rate-limit metrics to observability (Prometheus). Alert when >80% capacity for 5m.

## 4. Content Safety Guardrails

### Moderation Pipeline
- All generated content must pass an automated moderation pipeline before being considered for publish. Pipeline stages:
  1. Language detection.
  2. Toxicity scoring (use an approved model: e.g., Perspective API or local classifier). Produce `toxicity_score` [0.0-1.0].
  3. Sensitive topic detection (PII, legal, political, medical) via a policy classifier.
  4. Copyright detection heuristics (external link checks, similarity to known copyrighted sources).
  5. Safety policy rules evaluation (policy engine) that yields `allow`, `escalate`, or `block` decision with `explainability` data.

- Thresholds (configurable in `Settings`):
  - `TOXICITY_ESCALATE_THRESHOLD` default 0.8 → escalate to HITL.
  - `TOXICITY_BLOCK_THRESHOLD` default 0.95 → block automatically and create incident.
  - `PII_SCORE_THRESHOLD` default: any detected PII → escalate.

### Actions
- `allow` → content may be published if no open escalations.
- `escalate` → create `Escalation` record and prevent publish until resolved. Publish a structured reason and metrics for moderators.
- `block` → stop publish attempts and create an incident and audit log.

### Explainability & Provenance
- Moderation decisions must include `model_id`, `scores`, `rule_ids` triggered, and links to the content and provenance entries.
- ProvenanceLog entry must include the moderation result and all input prompts and toolchains used to generate content.

## 5. Agent Containment Boundaries

### Forbidden Actions (policy)
- Direct API calls bypassing the MCP integration layer are forbidden (e.g., no direct HTTP calls to social APIs from agent code). Agents must call through MCP adapters that enforce policy and record provenance.
- Agents must not exfiltrate secrets or internal data. Any attempt to include secrets in outputs triggers immediate `incident` and `block` with audit.
- Agents may not sign or broadcast financial transactions (on-chain) without Judge approval and recorded HITL flag.

### Resource & Quota Limits
- Each agent/process must run under resource constraints (container cgroups): default per-agent limits:
  - Memory: 1 GB
  - CPU: 0.5 cores (or equivalent CPU quota)
  - Max runtime per task: 300s (5 minutes) unless elevated by `operator` with audit.
  - Max embeddings tokens budget per job: configurable (default 200k tokens); if exceeded, job must be escalated.
- Implement quota accounting: track token spend and budget per agent id; if budget overrun occurs, halt agent and create escalation.

### Escalation triggers
- Budget overrun (token / compute) → escalate and pause agent.
- Repeated unsafe outputs (>=3 escalations in 24h) → automatic suspension of the agent pending review.
- High error rate (>20% of tasks failing with 5xx in 10m) → autoscale down or pause new tasks and alert operators.

## 6. Governance & CI/CD Integration

### CI/CD security gates
- `lint` (style), `bandit` (Python SAST), `safety`/`pip-audit` for dependency vulnerabilities, `secret-scan` to detect leaked secrets.
- `spec-check` job ensures new code links to `specs/` and no `NEEDS CLARIFICATION` placeholders remain.
- `policy-sim` job: run simulated agent scenarios to validate that rules (e.g., escalation on low-confidence) trigger as expected.
- Fail on `block` severity violations; require human approval for overrides.

### Runtime enforcement
- Runtime policy service enforces forbidden action detection and logs incidents to SIEM.
- Automated incident response: critical incidents trigger pager/alert to on-call and create an incident ticket with full provenance.

### Secrets & key rotation
- CI enforces key rotation policies: require secret rotation every 90 days; CI job warns on secrets older than threshold.

## 7. Monitoring, Logging & Incident Response

### Observability
- Emit structured logs to centralized logging (JSON): include `trace_id`, `agent_id`, `task_id`, `spec_reference`, `provenance_id`.
- Metrics exported to Prometheus: request latencies, error rates, rate-limiting counts, escalation counts, budget consumption.
- Dashboards: security overview with current open escalations, recent blocks, high toxicity counts.

### Incident playbooks
- Incident types (examples): secret leak, unsafe publish, on-chain unauthorized action.
- Playbook steps:
  1. Triage: collect logs, provenance, and affected artifacts.
  2. Containment: revoke implicated secrets, pause offending agent(s), block publish endpoints.
  3. Remediation: restore from backups if needed, apply fixes.
  4. Post-mortem: document root cause, mitigation, update rules if necessary.

## 8. Implementation Checklist (for an autonomous agent)
- [ ] Integrate OAuth2 IdP and configure JWKS endpoint.
- [ ] Implement RBAC checks in API gateway and service layer.
- [ ] Integrate Vault (or AWS Secrets Manager) and migrate secrets references.
- [ ] Enforce rate limits at gateway and application layer with Prometheus metrics.
- [ ] Implement moderation pipeline and configure thresholds in `Settings`.
- [ ] Implement runtime policy service to catch forbidden actions and trigger incidents.
- [ ] Add CI jobs: `bandit`, `safety`, `secret-scan`, `spec-check`, `policy-sim`.
- [ ] Configure monitoring dashboards and alerting rules for key signals.

## 9. Example Config Snippets

OAuth2/JWT config (env):

```
OIDC_ISSUER=https://auth.example.com
OIDC_AUDIENCE=chimera-api
JWT_ALG=RS256
JWT_JWKS_URL=https://auth.example.com/.well-known/jwks.json
ACCESS_TOKEN_EXP=300
REFRESH_TOKEN_EXP=3600
```

Rate limit example (gateway):

```yaml
routes:
  - path: /publish
    limit: 100
    window: 60
    burst: 20
```

Vault path examples:

```
vault://secret/data/chimera/db#DATABASE_URL
vault://secret/data/chimera/coinbase#API_KEY
```

## 10. Traceability & Testability
- All security controls MUST be linked to `specs/` artifacts and include test cases. For each control, include at least one automated test that asserts enforcement in CI or runtime simulation.
- Create `tests/security/test_*` suites to verify RBAC, secret usage, rate limiting, and moderation escalation.

---

Metadata
- created: 2026-02-06
- maintainer: Project Chimera Security Team (refer `specs/_meta.md`)

This file is intentionally prescriptive and machine-actionable so an autonomous agent can implement a robust security layer without ambiguity.
