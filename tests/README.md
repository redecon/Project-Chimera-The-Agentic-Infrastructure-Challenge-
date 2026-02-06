## Tests – TDD Safety Net
### Purpose
This folder contains the initial Test‑Driven Development (TDD) scaffolding for Project Chimera. The tests are intentionally designed to fail at this stage. Their role is to define the “empty slots” that the AI agents must later fill, ensuring that implementation work is guided by clear contracts and specifications.

## Files
### test_trend_fetcher.py  
Validates that the trend data structure returned by the trend_fetcher module matches the API contract defined in technical.md.

**Expected contract example:**

json
{
  "trend_id": "string",
  "name": "string",
  "popularity_score": "float",
  "timestamp": "ISO 8601 string"
}

### test_skills_interface.py  
Validates that the skills_interface module accepts the correct parameters and returns results in the expected format.
**Expected contract example:**

```bash
run_skill(skill_name: str, input_data: dict) -> dict
```

## Governance Note
These tests are deliberately failing until the corresponding modules are implemented. Their existence provides traceability between the specification (technical.md) and the implementation. This approach enforces governance discipline: we know the AI agent has built the right thing only when these tests pass.

By defining contracts upfront, we create a safety net for the AI swarm, ensuring that future development aligns with agreed standards.

## Usage
Run the tests with:

```bash
pytest tests/
```
At this stage, failures are expected and indicate that the safety net is correctly in place.