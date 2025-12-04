# Service Atlas MCP Server

## Purpose
This MCP server exposes read-only tools and resources for exploring a Service Atlas API: browsing teams, listing services for a team, searching services by name, and seeing which teams own a service.

## Capabilities
- Prompts that guide the AI on how to complete common tasks using the tools/resources
  - `get_all_teams`
  - `get_services_by_team`
  - `find_service_by_name`
  - `find_which_team_owns_a_service`

- Tools (read-only)
  - `get_all_teams()` → GET `/teams` (auto-paginates up to 200 results)
  - `get_services_by_team(team_id)` → GET `/teams/{team_id}/services`
  - `find_service_by_name(query)` → GET `/services/search?query={query}`
  - `get_teams_by_service(service_id)` → GET `/services/{service_id}/teams`

- Resources (MCP resources namespace)
  - `serviceatlas://teams` → All teams
  - `serviceatlas://teams/{team_id}/services` → Services by team
  - `serviceatlas://services/search/{query}` → Search services by name
  - `serviceatlas://services/{service_id}/teams` → Teams by service

## Resource Scheme
Resources use the `serviceatlas://` scheme so that requests are routed specifically to this server.

## Use Cases
Each use case is implemented with a prompt, a tool, and an equivalent resource.
- List all teams → tool `get_all_teams` or resource `serviceatlas://teams`
- List all services that belong to a team → tool `get_services_by_team` or resource `serviceatlas://teams/{team_id}/services`
- Find a service by name → tool `find_service_by_name` or resource `serviceatlas://services/search/{query}`
- Find which team owns a service → tool `get_teams_by_service` or resource `serviceatlas://services/{service_id}/teams`

## Running and Testing Locally

Use the Model Context Protocol Inspector to connect and test this MCP server.

Prereqs: Node.js installed.

1) Start the Inspector from the project root:
```
npx @modelcontextprotocol/inspector
```

2) In the Inspector UI, add a new Server with:
- Command: `uv`
- Args: `run src/mcp_server.py`
- Environment:
  - `API_URL` → base URL of your Service Atlas API (e.g. `http://localhost:8080`)

3) Connect to the server from the Inspector and try the tools/resources listed above.

If you run a local Service Atlas API for testing, make sure it’s reachable at the URL you put into `API_URL`.

## References
- MCP Resources: https://modelcontextprotocol.io/specification/2025-06-18/server/resources
- FastMCP Docs: https://gofastmcp.com/getting-started/welcome