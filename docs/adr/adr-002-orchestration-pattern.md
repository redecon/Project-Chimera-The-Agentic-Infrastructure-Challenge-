# ADR 002 — Orchestration Pattern: Planner / Worker / Judge Swarm

Date: 2026-02-06
Status: Accepted

## Context
Chimera's architecture must coordinate complex, multi-step tasks that include planning, tool invocation (skills), validation, and safety gating. The system must support delegation to specialized components, human-in-the-loop checks, and traceable decision logs.

## Decision
Use a hierarchical swarm pattern composed of:
- Planner(s): high-level goal decomposition and intent generation.
- Worker(s): specialized skill executors responsible for single-purpose actions (download, transcribe, reconcile).
- Judge: centralized policy and safety adjudicator responsible for HITL escalation, approval gating, and on-chain attestation.

This pattern enforces separation of concerns, scales horizontally by adding worker types, and centralizes policy decisions in the Judge component.

## Alternatives Considered
- Single-agent monolith: one agent performing planning, execution, and validation. Rejected due to poor separation of concerns, harder auditing, and difficult scaling.
- Sequential chain of agents: a pipeline of agents each performing a single step passing outputs along. Rejected because error handling and policy checks become scattered and harder to centralize; recovery is more complex.

## Consequences
- Pros:
  - Modularity: new skills can be added without changing planners or judge logic.
  - Clear audit trails: Judge centralizes decisions and records provenance.
  - Scalability: Workers can scale independently based on workload.
- Cons:
  - Increased system complexity and need for reliable messaging and orchestration.
  - Latency overhead due to orchestration and safety checks.

## Non-Goals
- Not aiming to implement fully decentralized consensus among planners or judges—Judge is intentionally authoritative within the swarm.

---
References: specs/rules_intent.md, specs/002-trend-ingestion/spec.md
