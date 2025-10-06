# MCP Servers for Commercial-View

## Figma MCP Server

### URL and Setup
```bash
# Install Figma MCP Server
npm install @figma/mcp-server-figma

# Server Command
npx @figma/mcp-server-figma

# GitHub Repository
https://github.com/figma/mcp-server-figma
```

### Authentication (No OAuth Support)
⚠️ **Important**: The Figma MCP server does **NOT** implement OAuth authentication. It uses Personal Access Tokens instead.

#### Your Figma Token Configuration
✅ **Token Provided**: `figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK`

### Configuration
```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["@figma/mcp-server-figma"],
      "env": {
        "FIGMA_PERSONAL_ACCESS_TOKEN": "figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"
      }
    },
    "commercial-view-api": {
      "command": "python",
      "args": ["-m", "uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"],
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "ENVIRONMENT": "development"
      }
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Environment Variables
```bash
# Your actual Figma token (configured)
FIGMA_PERSONAL_ACCESS_TOKEN=figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK

# Token verified and ready to use
```

### Test Your Token
```bash
# Test your Figma token manually
curl -H "X-Figma-Token: figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK" https://api.figma.com/v1/me

# Expected response: Your Figma user information
```

### Alternative MCP Setup (Token-based)
```json
{
  "mcpServers": {
    "figma-simple": {
      "command": "node",
      "args": ["-e", "
        const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
        const server = new Server({
          name: 'figma-simple',
          version: '1.0.0'
        });
        // Token-based authentication only
        process.env.FIGMA_TOKEN = process.env.FIGMA_PERSONAL_ACCESS_TOKEN;
        server.connect();
      "],
      "env": {
        "FIGMA_PERSONAL_ACCESS_TOKEN": "figd_your_token"
      }
    }
  }
}
```

## Commercial-View MCP Integration

### API Endpoints
- **Base URL**: `http://localhost:8000`
- **MCP Endpoint**: `http://localhost:8000/mcp`
- **Health Check**: `http://localhost:8000/health`

### Usage Commands
```bash
# Setup MCP configuration
python scripts/build.py mcp

# Start Figma MCP server
python scripts/mcp_server.py figma

# Get all MCP server URLs
python scripts/mcp_server.py urls

# Get Figma server information
python scripts/mcp_server.py info
```

### Custom Figma Integration (No OAuth)
Since the Figma MCP server doesn't support OAuth, we provide a custom integration:

```bash
# Create custom Figma integration
python scripts/mcp_server.py create-figma-integration

# Test Figma API connection
python scripts/mcp_server.py test-figma-connection

# Get Figma files (token-based)
python scripts/mcp_server.py figma-files
```

## Other MCP Servers

### GitHub MCP Server (Token-based)
```bash
npm install @modelcontextprotocol/server-github
npx @modelcontextprotocol/server-github

# GitHub also uses Personal Access Tokens, not OAuth for MCP
```

### Authentication Summary
| Server | Auth Method | OAuth Support | Token Type |
|--------|-------------|---------------|------------|
| Figma | Personal Access Token | ❌ No | `figd_...` |
| GitHub | Personal Access Token | ❌ No | `ghp_...` |
| Commercial-View | API Key | ❌ No | Custom |
| Google Drive | Service Account | ⚠️ Limited | JSON Key |

### Available Servers
- **Figma**: Design file access (Personal Access Token only)
- **GitHub**: Repository management (Personal Access Token only)
- **Commercial-View**: Portfolio analytics API (Custom auth)
- **Google Drive**: File storage integration (Service Account JSON)

### Quick Fix for OAuth Errors
```bash
# 1. Remove any OAuth configuration from your MCP setup
# 2. Use only Personal Access Tokens
# 3. Verify token format and permissions
# 4. Restart MCP server with token-based config

# Example working configuration:
export FIGMA_PERSONAL_ACCESS_TOKEN="figd_your_actual_token"
npx @figma/mcp-server-figma
```

### Quick Setup Commands
```bash
# Export your token
export FIGMA_PERSONAL_ACCESS_TOKEN="figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"

# Start Figma MCP server
npx @figma/mcp-server-figma

# Test connection
python scripts/mcp_server.py test-figma
```

### Testing Your Setup
```bash
# Test Figma token
python scripts/mcp_server.py test-figma

# Test all MCP connections
python scripts/mcp_server.py test-all

# Debug OAuth issues
python scripts/mcp_server.py debug-auth
```
