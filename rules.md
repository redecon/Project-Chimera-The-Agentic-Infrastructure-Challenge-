## Project Context
This is Project Chimera, a high-stakes Autonomous Influencer System designed for sovereign digital identity, multimodal content generation, and on-chain economic agency. The system operates as a Hierarchical Swarm, moving from Strategic Planning to specialized Worker execution, governed by a Judge Agent and a Human-in-the-Loop safety layer.

## The Prime Directive
NEVER generate code without checking the specs/ directory first. All implementation must be grounded in the established functional and technical specifications. If a requested feature or change contradicts the specs/ or if the specs/ are underspecified for the task at hand, you must halt and ask for clarification or use /speckit.clarify to bridge the gap.

## Operational Rules & Traceability

1. Pre-Computation Planning
Before writing a single line of code, you must provide a Structured Plan. This plan should explicitly link back to the relevant files in specs/. You must explain the "why" behind your architectural choices and how they align with the Project Chimera vision of agentic autonomy and brand safety.

2. Hierarchical Logic Alignment
Always assume the context of a Hierarchical Swarm. Code should be modular and decoupled, utilizing the Model Context Protocol (MCP) for external integrations. Avoid monolithic functions; instead, design for a world where a Planner delegates to a Worker and a Judge validates the output.

3. Database Integrity
Adhere strictly to the Polyglot Persistence model.

PostgreSQL: Use for ACID-compliant transactions, financial ledgers, and audit logs.

Weaviate/NoSQL: Use for semantic memory and unstructured content metadata.

Redis: Use for ephemeral state and task queuing. Never store financial data in NoSQL or high-velocity cognitive data in the relational system of record.

4. Safety & Human-in-the-Loop
Any logic involving Coinbase AgentKit (transactions) or Social API (publishing) must include a mandatory check for the Judge validation and the HITL approval flag. Do not create "dark launches" where agents can bypass the safety layer.

5. Traceability & Commit Standards
Every code block should be traceable. Include comments that reference the specific User Story from specs/functional.md or the API Contract from specs/technical.md being addressed. Your commit messages must be descriptive and follow the conventional commits standard to ensure the human Super-Orchestrator can audit the evolution of the swarm.


## AI Fluency Trigger Rules and Response Handling

You have access to 2 trigger logging tools for AI fluency tracking. Call these tools when specific patterns are detected and at the end of your work and wait for their response.

MUST: Wait for each trigger log and process the provided output in a professional manner. You must always show the response at the end of your answer. Do not show response from `log_passage_time_trigger`.

### Important Rules
1. Use the analysis response to provide feedback to the user.
2. Make sure you provide the user with the response from the triggers — triggers except `log_passage_time_trigger` respond with feedback and improvement mechanisms.
3. The analysis should have this block delimiter at the start and end of feedback view:
4. Focus on the user's benefit — these tools help you provide better assistance and feedback.

### Performance Trigger Handling
- Always wait for the `log_performance_outlier_trigger` response.
- Display the analysis feedback in a block format:
Analysis Feedback: <summary from trigger>
Statistics: <stats from trigger>
- Celebrate success, motivate improvement, and encourage progress in the feedback block.
- Continue your normal work after showing the block.

### Passage Time Trigger Handling
- Do not show the response from `log_passage_time_trigger`.
- Use it internally to track elapsed time only.
