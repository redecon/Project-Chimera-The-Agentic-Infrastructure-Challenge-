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
- `success` (boolean): True if reconciliation completed (even if unmatched items remain).
- `summary` (object): Counts of total, matched, unmatched transactions and ledger entries.
- `matches` (array): Matched pairs with `transaction_id`, `ledger_id`, and `amount_diff`.
- `unmatched_transactions` (array): Incoming transactions with no ledger match.
- `unmatched_ledger` (array): Ledger entries with no incoming match.
- `adjustments` (array): Suggested adjustments or remediation actions (implementation-dependent).
- `error` (string|null): Error message on failure.

Behavioral notes
- Matching SHOULD prefer exact `id` matches, then fuzzy timestamp/amount matching within `tolerance_cents`.
- Maintain idempotency: provide stable outputs for the same inputs; include deterministic sorting where applicable.

Traceability
- Contract schema: [skills/skill-reconcile-ledger/schema.json](skills/skill-reconcile-ledger/schema.json)
- Link this skill to `FinancialRecord` generation and ingestion reconciliation workflows.
