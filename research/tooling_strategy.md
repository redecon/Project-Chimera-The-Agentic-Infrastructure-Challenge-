## The Developer Autonomy Framework
To fulfill the mandate of Project Chimera, the internal AI agents (the "Co-pilots") must be equipped with a robust set of Developer Tools that allow them to move beyond simple text prediction and into active codebase management. This strategy utilizes the Model Context Protocol (MCP) to provide the agents with a standardized interface for interacting with the local environment, version control systems, and external documentation.

## Core Developer MCP Configuration
The following MCP servers are selected as the foundational toolkit for the Chimera development lifecycle. These tools allow the agent to perform autonomous refactoring, verify system states, and manage the evolution of the specs/ and src/ directories.

1. Filesystem-MCP (The Hands)
This server provides the agent with the ability to read, write, and organize the project structure. It is the primary tool for implementing the "Spec-Driven" mandate, as it allows the agent to scan the specs/ directory before generating implementation files.

**Scope:** Restricted to the project root directory only.

**JSON Config:**

JSON
"filesystem": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"]
}

2. Git-MCP (The Memory)
The Git-MCP server ensures that every significant change is recorded. It allows the agent to create branches for new features, stage changes, and write descriptive commit messages that reference specific functional requirements.

**Scope:** Restricted to the Project Chimera repository.

**JSON Config:**

JSON
"git": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github", "--repository", "project-chimera"]
}

3. Fetch-MCP (The Researcher)
Used during the /speckit.plan phase, this tool retrieves and converts web documentation into Markdown to ensure implementations use current API versions (e.g., the latest Coinbase AgentKit).

**Scope:** Restricted to whitelisted documentation domains (e.g., docs.cloud.coinbase.com, modelcontextprotocol.io).

**JSON Config:**

JSON
"fetch": {
  "command": "uvx",
  "args": ["mcp-server-fetch"]
}

## Hybrid Persistence Tools (Database-MCP)
Given the Polyglot Persistence architecture, the developer agent requires direct access to inspect and validate database states during implementation.

4. Postgres-MCP (Relational Audit)
Used for creating migrations and verifying the SQL System of Record (Asset Metadata and Financial Ledgers).

**Scope:** Restricted to the chimera_dev database instance.

**JSON Config:**

JSON
"postgres": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost:5432/chimera_dev"]
}

5. Weaviate-MCP (Semantic Verification)
Used to audit vector embeddings and verify that the "Long-Term Episodic Memory" is correctly storing and retrieving persona-aligned context.

**Scope:** Restricted to the local Weaviate cluster and specified collections.

**JSON Config:**

JSON
"weaviate": {
  "command": "uvx",
  "args": ["mcp-weaviate", "--connection-type", "local", "--host", "localhost", "--port", "8080"]
}

## Tooling Governance and Safety
Every tool invocation is governed by The Prime Directive established in .cursor/rules. The agent is prohibited from using the filesystem-mcp to overwrite files without first stating its plan. Any tool interacting with the network or databases is subject to a "Reasoning Trace" requirement, documenting the necessity of the call for audit by the human Super-Orchestrator.