# ADR 003 — Security Strategy: OAuth/JWT + Vault

Date: 2026-02-06
Status: Accepted

## Context
Project Chimera must protect sensitive keys, enforce role-based access, and ensure auditable authentication and authorization for both human users and services. Agents will perform actions with safety and audit requirements, including on-chain attestations and financial write operations.

## Decision
Adopt OAuth2 with JWTs for authentication and RBAC for authorization, combined with a secrets vault for secret storage:
- OAuth2 (Authorization Code for humans, Client Credentials for services) with RS256-signed JWTs; publish JWKS for verification.
- Role-Based Access Control: `operator`, `moderator`, `developer`, `service` roles with fine-grained policies.
- Secrets stored and rotated in HashiCorp Vault or AWS Secrets Manager; services retrieve secrets via short-lived credentials.

## Alternatives Considered
- Basic API keys: considered for simplicity but rejected due to poor rotation, limited scoping, and increased risk if leaked.
- Storing secrets in environment variables or repo: rejected due to security and compliance risks.

## Consequences
- Pros:
  - Strong auditability (JWT claims, audit logs, vault audit devices).
  - Easier secrets rotation and centralized policy enforcement.
- Cons:
  - Operational overhead to run and maintain IdP and Vault.
  - Integration work required for services to use dynamic secret retrieval.

## Non-Goals
- Not planning to rely on static, unrotated API keys or to store secrets in plaintext in the repository.

---
References: specs/security.md, specs/rules_intent.md
