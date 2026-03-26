# Service Atlas MCP Server

## Purpose
This MCP server exposes tools and resources for exploring a Service Atlas API: browsing teams, listing services for a team, searching services by name, seeing which teams own a service, and exploring service dependencies, tech debt, and releases.

## Capabilities
- Prompts that guide the AI on how to complete common tasks using the tools/resources
  - `get_all_teams`
  - `get_services_by_team`
  - `find_service_by_name`
  - `find_which_team_owns_a_service`
  - `get_debt`
  - `get_releases`
  - `get_service_dependencies_and_dependents`
  - `get_service_risk`
  - `analyze_service_risk_and_impact`

- Tools
  - `get_all_teams()` → GET `/teams` (auto-paginates up to 200 results)
  - `get_services_by_team(team_id)` → GET `/teams/{team_id}/services`
  - `find_service_by_name(query)` → GET `/services/search?query={query}`
  - `get_teams_by_service(service_id)` → GET `/services/{service_id}/teams`
  - `get_debt()` → GET `/reports/services/debt`
  - `get_debts_for_service(service_id)` → GET `/services/{service_id}/debt`
  - `get_releases(start, end)` → GET `/releases/{start}/{end}`
  - `get_service_dependencies(service_id)` → GET `/services/{service_id}/dependencies`
  - `get_service_dependents(service_id)` → GET `/services/{service_id}/dependents`
  - `create_dependency(service_id, dependency_id, version)` → POST `/services/{service_id}/dependency`
- `get_service_risk(service_id)` → GET `/reports/services/{service_id}/risk`
  Returns a JSON risk report containing:
  - `changeRisk`: A heuristic score (0-100) and risk level (low/medium/high) indicating the potential system-wide impact of failure or modification.
  - `healthRisk`: Current condition metrics including dependency count and technical debt count by category.

- Resources (MCP resources namespace)
  - `serviceatlas://teams` → All teams
  - `serviceatlas://teams/{team_id}/services` → Services by team
  - `serviceatlas://services/search/{query}` → Search services by name
  - `serviceatlas://services/{service_id}/teams` → Teams by service
  - `serviceatlas://debts` → Debt report
  - `serviceatlas://debts/{service_id}` → Debts by service
  - `serviceatlas://releases/{start}/{end}` → Releases in date range
  - `serviceatlas://services/{service_id}/dependencies` → Service dependencies
  - `serviceatlas://services/{service_id}/dependents` → Service dependents
  - `serviceatlas://services/{service_id}/risk` → Service risk report

## Resource Scheme
Resources use the `serviceatlas://` scheme so that requests are routed specifically to this server.

## Use Cases
Each use case is implemented with a prompt, a tool, and an equivalent resource.
- List all teams → tool `get_all_teams` or resource `serviceatlas://teams`
- List all services that belong to a team → tool `get_services_by_team` or resource `serviceatlas://teams/{team_id}/services`
- Find a service by name → tool `find_service_by_name` or resource `serviceatlas://services/search/{query}`
- Find which team owns a service → tool `get_teams_by_service` or resource `serviceatlas://services/{service_id}/teams`
- Get tech debt report → tool `get_debt` or resource `serviceatlas://debts`
- Get tech debt for a service → tool `get_debts_for_service` or resource `serviceatlas://debts/{service_id}`
- Get releases in a date range → tool `get_releases` or resource `serviceatlas://releases/{start}/{end}`
- Get service dependencies → tool `get_service_dependencies` or resource `serviceatlas://services/{service_id}/dependencies`
- Get service dependents → tool `get_service_dependents` or resource `serviceatlas://services/{service_id}/dependents`
- Create a service dependency → tool `create_dependency`
- Get service risk report → tool `get_service_risk` or resource `serviceatlas://services/{service_id}/risk`. 
  This report is used to answer the question: "If this service changes or fails, how broadly could that impact the system?" It provides a heuristic score based on the service's position in the dependency graph.

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