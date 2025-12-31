# MCP Server Configuration

This project uses Model Context Protocol (MCP) servers to extend agent capabilities.

## Configured MCP Servers

### Tavily Search
- **Purpose**: Web search and research intelligence for the Scout agent
- **Configuration**: `.claude/mcp_config.json`
- **URL**: `https://mcp.tavily.com/mcp/?tavilyApiKey=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`

## Setup Instructions

### For Claude Code (CLI)
The MCP configuration is already set up in `.claude/mcp_config.json`. Claude Code will automatically load this configuration when working in this directory.

### For Claude Desktop
1. Open Claude Desktop settings
2. Navigate to the "Developer" or "MCP" section
3. Add the Tavily MCP server:
   ```json
   {
     "mcpServers": {
       "tavily": {
         "url": "https://mcp.tavily.com/mcp/?tavilyApiKey=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",
         "transport": "sse"
       }
     }
   }
   ```
4. Restart Claude Desktop

## Environment Variables

Add to your `.env` file:
```bash
TAVILY_API_KEY=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
```

## Available MCP Tools

Once configured, the following tools are available via Tavily MCP:
- `tavily_search`: Web search with AI-optimized results
- `tavily_extract`: Extract and summarize content from URLs
- `tavily_news`: Search recent news articles

## Testing the Integration

To verify the MCP server is working:
```python
# The Scout agent will automatically use Tavily MCP when available
from agents.scout import Scout

scout = Scout(config)
result = scout.invoke({
    "topic": "EU data sovereignty regulations"
})
```

## Security Notes

- The API key is embedded in the MCP URL for simplicity
- For production: Consider using environment variable substitution
- Rotate API keys regularly
- Monitor usage via Tavily dashboard: https://app.tavily.com/

## Troubleshooting

**MCP server not connecting:**
- Verify internet connectivity
- Check API key is valid at https://app.tavily.com/
- Ensure Claude Code/Desktop is up to date

**Tools not appearing:**
- Restart Claude Desktop
- For Claude Code: Check `.claude/mcp_config.json` is valid JSON
- Verify the URL is accessible

## Learn More

- MCP Specification: https://modelcontextprotocol.io/
- Tavily API Docs: https://docs.tavily.com/
- Claude MCP Guide: https://docs.anthropic.com/claude/docs/mcp
