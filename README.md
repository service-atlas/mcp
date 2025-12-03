# MCP Server

## Purpose
This MCP Server provides tools to communicate with an instance of a service atlas API.

## Resource Specification
The resources use a custom http-esque resource specification in the format of `servicemap://` so that requests from the client 
are directed only to the service atlas mcp.

## Use Cases
Each use case is implemented with a prompt, a tool, and a resource
### List All Services that belong to a Team
This use case lists all services that belong to a team. It calls the `/teams/{teamId}/services` endpoint of the service atlas api.`



## Testing

To test the mcp server locally, use the `ModelContextProtocolInspector`.
This tool requires `node` and can be run with the following command from the root of the project:

```bash
npx @modelcontextprotocol/inspector
```
The command to start this mcp server is `uv run` with arguments `src/mcp_server.py`.

Once the mcp inspector is running, navigate to the localhost url that is displayed in the terminal.
You will need to input the run command as `go run` and the optional arguments as `./mcp/cmd/service-dependency-mcp`.

**Note: You will need to set the `API_URL` environment variable to the url of the service dependency api.**

To facilitate testing, a docker compose file is provided in the service map api project. You can run the docker compose file with the following command:

```bash
docker compose -f service.compose.yml up -d
```

Then you can run the `Sample Service Map` folder in the Bruno collection. This will populate the docker compose database with sample data via the api.

## References
- [BruceTraining MCP Example](https://github.com/BruceTraining/MCP-Oreilly-2)
- [MCP Resources](https://modelcontextprotocol.io/specification/2025-06-18/server/resources)
- [FastMCP Docs](https://gofastmcp.com/getting-started/welcome)