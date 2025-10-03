# Meta Business Suite Integration

Claude Code can help you document and automate Meta Business workflows.

## Meta Business Context

- Platform APIs: Facebook Graph API, Instagram Basic Display API
- Content types: Posts, Stories, Reels, Ads
- Analytics: Insights API for performance metrics
- Business Manager: Ad accounts, Pages, Instagram accounts

## Documentation Requirements for Meta Integrations

- Include API version numbers
- Document rate limits and quotas
- Provide sandbox testing examples
- Include webhook configuration steps
- Document token refresh procedures

## Setup

### Prerequisites

1. Meta Business Suite account
2. App created in Meta Developer Portal
3. Required permissions granted

### Authentication

```javascript
// Example authentication setup
const accessToken = process.env.META_ACCESS_TOKEN;
const apiVersion = 'v18.0';
const baseUrl = `https://graph.facebook.com/${apiVersion}`;
```

### API Integration

```javascript
// Example API call
async function getPageInsights(pageId) {
  const response = await fetch(
    `${baseUrl}/${pageId}/insights?access_token=${accessToken}`
  );
  return await response.json();
}
```

## Security

Always store Meta access tokens in environment variables:

```bash
META_ACCESS_TOKEN=your-token-here
META_APP_ID=your-app-id
META_APP_SECRET=your-app-secret
```
