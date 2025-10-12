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

#### Figma Token Issue - 403 Forbidden Error

❌ **Current Status**: Token `figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK` is returning 403 Forbidden

### Troubleshooting 403 Error

#### Possible Causes

1. **Token Expired**: Personal access tokens can expire
2. **Invalid Token**: Token may be malformed or revoked
3. **Insufficient Permissions**: Token lacks required scopes
4. **Account Issues**: Figma account may have restrictions

#### Steps to Fix

1. **Generate New Token**:
   - Go to [Figma Settings > Personal Access Tokens](https://www.figma.com/settings/account)
   - Delete the old token: `figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK`
   - Create new token with name "Commercial-View MCP"
   - Copy the new token (starts with `figd_`)

2. **Verify Token Format**:

   ```bash
   # Valid token format: figd_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   # Length: approximately 45-50 characters
   # Starts with: figd_
   ```

3. **Test New Token**:

   ```bash
   # Replace YOUR_NEW_TOKEN with the actual new token
   curl -H "X-Figma-Token: YOUR_NEW_TOKEN" https://api.figma.com/v1/me
   
   # Expected success response:
   # {"id":"123456789","email":"your-email@domain.com","handle":"YourName"}
   ```

### Configuration Template

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["@figma/mcp-server-figma"],
      "env": {
        "FIGMA_PERSONAL_ACCESS_TOKEN": "REPLACE_WITH_NEW_FIGMA_TOKEN"
      }
    },
    "commercial-view-api": {
      "command": "python",
      "args": ["-m", "uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"],
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "ENVIRONMENT": "production"
      }
    },
    "commercial-view-sse": {
      "url": "http://localhost:8000/sse",
      "authentication": {
        "type": "none"
      }
    }
  }
}
```

### Environment Variables

```bash
# OLD TOKEN (403 Forbidden - DO NOT USE)
# FIGMA_PERSONAL_ACCESS_TOKEN=figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK

# NEW TOKEN (Replace with your new token)
FIGMA_PERSONAL_ACCESS_TOKEN=REPLACE_WITH_NEW_FIGMA_TOKEN

# Commercial View API Configuration
COMMERCIAL_VIEW_API_URL=http://localhost:8000
COMMERCIAL_VIEW_SSE_URL=http://localhost:8000/sse
```

### Token Validation

```bash
# Test your new token (replace with actual token)
curl -H "X-Figma-Token: YOUR_NEW_TOKEN" https://api.figma.com/v1/me

# If successful, update all configurations:
export FIGMA_PERSONAL_ACCESS_TOKEN="YOUR_NEW_TOKEN"
```

### Required Actions

1. **Get New Figma Token**: Visit https://www.figma.com/settings/account
2. **Update Configuration**: Replace old token in all config files
3. **Test Connection**: Verify new token works before using MCP server
4. **Restart Services**: Restart MCP server with new token

### Alternative Configuration (Disable Figma Temporarily)

```json
{
  "mcpServers": {
    "figma": {
      "disabled": true,
      "reason": "Token expired - awaiting new token"
    },
    "commercial-view-api": {
      "command": "python",
      "args": ["-m", "uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"],
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "ENVIRONMENT": "production"
      }
    },
    "commercial-view-sse": {
      "url": "http://localhost:8000/sse",
      "authentication": {
        "type": "none"
      }
    }
  }
}
```

### Production Setup

```bash
# Set production Figma token
export FIGMA_PERSONAL_ACCESS_TOKEN="figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"

# Start Commercial-View API server
python server_control.py --port 8000

# Start Figma MCP server
npx @figma/mcp-server-figma

# Verify all endpoints
curl http://localhost:8000/health
```

### Integration Commands

```bash
# REQUIRED: Activate virtual environment first
source .venv/bin/activate

# Test current token (will show 403)
curl -H "X-Figma-Token: figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK" https://api.figma.com/v1/me

# After getting new token, test it:
# curl -H "X-Figma-Token: YOUR_NEW_TOKEN" https://api.figma.com/v1/me

# Check Commercial-View API status
python server_control.py --check-only --port 8000

# Monitor SSE stream
curl -N http://localhost:8000/sse
```

### Quick Test Commands

1. **Test Current Token**:

   ```bash
   curl -H "X-Figma-Token: figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK" https://api.figma.com/v1/me
   ```

2. **Get New Token**: Visit https://www.figma.com/settings/account

3. **Test New Token**:

   ```bash
   curl -H "X-Figma-Token: YOUR_NEW_TOKEN" https://api.figma.com/v1/me
   ```

4. **Update Configuration**: Replace token in config files manually

## Other MCP Servers

### GitHub MCP Server

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

### Server Overview

- **Figma**: Design file access (Personal Access Token only)
- **GitHub**: Repository management (Personal Access Token only)
- **Commercial-View**: Portfolio analytics API (Custom auth)
- **Google Drive**: File storage integration (Service Account JSON)

### OAuth Error Resolution

```bash
# 1. Remove any OAuth configuration from your MCP setup
# 2. Use only Personal Access Tokens
# 3. Verify token format and permissions
# 4. Restart MCP server with token-based config

# Example working configuration:
export FIGMA_PERSONAL_ACCESS_TOKEN="figd_your_actual_token"
npx @figma/mcp-server-figma
```

### Quick Setup

```bash
# Export your token
export FIGMA_PERSONAL_ACCESS_TOKEN="figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK"

# Start Figma MCP server
npx @figma/mcp-server-figma

# Test connection
python scripts/mcp_server.py test-figma
```

### Testing Commands

```bash
# Test Figma token
python scripts/mcp_server.py test-figma

# Test all MCP connections
python scripts/mcp_server.py test-all

# Debug OAuth issues
python scripts/mcp_server.py debug-auth
```

### Environment Setup

❌ **Issue**: Python command not found - virtual environment not activated

#### Simple Token Test

```bash
# Direct test - just run this one command:
curl -H "X-Figma-Token: figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK" https://api.figma.com/v1/me
```

### Expected Results

- **403 Forbidden**: Token is invalid/expired (need new token)
- **200 OK**: Token is working (rare, given previous errors)

### New Token Process

1. **Visit**: https://www.figma.com/settings/account
2. **Delete old token**: `figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK`
3. **Create new token**: Name it "Commercial-View MCP"
4. **Copy new token**: Will start with `figd_`
5. **Test new token**:

   ```bash
   curl -H "X-Figma-Token: YOUR_NEW_TOKEN_HERE" https://api.figma.com/v1/me
   ```

### Final Configuration

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["@figma/mcp-server-figma"],
      "env": {
        "FIGMA_PERSONAL_ACCESS_TOKEN": "YOUR_NEW_TOKEN_HERE"
      }
    },
    "commercial-view-api": {
      "command": "python",
      "args": ["-m", "uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"],
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "ENVIRONMENT": "production"
      }
    },
    "commercial-view-sse": {
      "url": "http://localhost:8000/sse",
      "authentication": {
        "type": "none"
      }
    }
  }
}
```

### Environment Template

```bash
# Replace with your new token
FIGMA_PERSONAL_ACCESS_TOKEN=YOUR_NEW_TOKEN_HERE

# Commercial View API Configuration
COMMERCIAL_VIEW_API_URL=http://localhost:8000
COMMERCIAL_VIEW_SSE_URL=http://localhost:8000/sse
```

### Status Summary

- ❌ **Figma Token**: `figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK` (Invalid - 403 Error)
- ⏳ **Action Required**: Get new token from Figma settings
- ✅ **Commercial-View API**: Ready on `http://localhost:8000`
- ✅ **SSE Endpoint**: Available at `http://localhost:8000/sse`

### Final Test Commands

```bash
# 1. Test current (expired) token
curl -H "X-Figma-Token: figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK" https://api.figma.com/v1/me

# 2. Test Commercial-View API (should work)
curl http://localhost:8000/health

# 3. After getting new Figma token, test it
# curl -H "X-Figma-Token: YOUR_NEW_TOKEN" https://api.figma.com/v1/me
```
      "authentication": {
        "type": "none"
      }
    }
  }
}
```

### Environment Variables Template

```bash
# Replace with your new token
FIGMA_PERSONAL_ACCESS_TOKEN=YOUR_NEW_TOKEN_HERE

# Commercial View API Configuration
COMMERCIAL_VIEW_API_URL=http://localhost:8000
COMMERCIAL_VIEW_SSE_URL=http://localhost:8000/sse
```

### Current Status Summary

- ❌ **Figma Token**: `figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK` (Invalid - 403 Error)
- ⏳ **Action Required**: Get new token from Figma settings
- ✅ **Commercial-View API**: Ready on `http://localhost:8000`
- ✅ **SSE Endpoint**: Available at `http://localhost:8000/sse`

### Simple Test Commands

```bash
# 1. Test current (expired) token
curl -H "X-Figma-Token: figd_eh6CUq7fBvqvmlWjPX875tdiyrkoPzC3s-TfrdVK" https://api.figma.com/v1/me

# 2. Test Commercial-View API (should work)
curl http://localhost:8000/health

# 3. After getting new Figma token, test it
# curl -H "X-Figma-Token: YOUR_NEW_TOKEN" https://api.figma.com/v1/me
```
