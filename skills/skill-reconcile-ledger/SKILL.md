Skill: reconcile-ledger

Purpose
- Reconcile a stream of incoming transactions against a canonical ledger snapshot to produce matched pairs, unmatched items, and a reconciliation summary. Intended for nightly or on-demand financial reconciliation workflows.

Schema
- Input / Output contract: [skills/skill-reconcile-ledger/schema.json](skills/skill-reconcile-ledger/schema.json)

Inputs
- `transactions` (array of transaction objects, required): Incoming transaction stream to reconcile. Each transaction includes `id`, `timestamp`, `amount`, `currency`, and optional `description` and `metadata`.
- `ledger_snapshot` (array of transaction objects, required): Canonical ledger entries used as the reconciliation target.
- `tolerance_cents` (integer, optional): Allowed cent-level tolerance for amount matching (default: 0).
- `currency` (string, optional): Currency to normalize amounts.

Outputs
- Success case: `success: true`, `summary`, `matches`, `unmatched_transactions`, `unmatched_ledger`, `adjustments`, `error: null`.
- Failure case: `success: false`, `error` (string) describing failure.

Error handling notes
- Possible error cases:
  - `InvalidInput`: missing required fields or malformed transaction objects.
  - `LedgerAccessError`: cannot read ledger snapshot (permission or connectivity issues).
  - `DBError`: database errors when attempting to persist reconciliation results.
  - `ToleranceMismatch`: configuration error leading to unexpected matching behavior.
  - `BudgetExceeded`: reconciliation job exceeded compute or billing budget.
- Behavior:
  - Validate input schema strictly; return `success: false` with `error` explaining invalid fields.
  - For transient DB errors, apply bounded retries with exponential backoff; after retries exhausted, return `success: false` and write diagnostic to audit logs and move work item to DLQ if applicable.
  - Ensure reconciliation is idempotent: include a stable `run_id` and avoid double-posting adjustments.

Dependencies
- Libraries: `psycopg2` or `asyncpg` for Postgres access, `decimal` for currency-safe math.
- External services: Coinbase AgentKit adapter (for on-chain verification when needed), accounting systems connectors.
- MCP: ledger API access must be via MCP connector that enforces approval for sensitive adjustments.

Example error responses
- Ledger access error:

```json
{ "success": false, "error": "Ledger access denied: permission error for snapshot 2026-02-05" }
```

- Invalid input:

```json
{ "success": false, "error": "Invalid input: transaction[0].amount is not a number" }
```

Behavioral notes
- Matching SHOULD prefer exact `id` matches, then fuzzy timestamp/amount matching within `tolerance_cents`.
- Maintain idempotency: provide stable outputs for the same inputs; include deterministic sorting where applicable.

Traceability
- Contract schema: [skills/skill-reconcile-ledger/schema.json](skills/skill-reconcile-ledger/schema.json)
- Link this skill to `FinancialRecord` generation and ingestion reconciliation workflows.
