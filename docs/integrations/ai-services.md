# AI Integrations

This document describes the AI service integrations available in the Commercial-View project.

## Overview

The project integrates with multiple AI services for enhanced functionality:

- **Google Gemini**: Advanced AI model integration
- **OpenAI**: GPT models and API access
- **Google Cloud**: Cloud AI services
- **Figma**: Design integration
- **HubSpot**: CRM and marketing automation

## Configuration

All AI service credentials should be configured via environment variables. Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

## Google Gemini Integration

### Setup

1. Create a project in Google AI Studio
2. Generate an API key
3. Add to your `.env` file:

```env
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_PROJECT_ID=your-gemini-project-id-here
```

### Usage

```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Your prompt here")
```

## OpenAI Integration

### Setup

1. Sign up at https://platform.openai.com
2. Create an API key
3. Add to your `.env` file:

```env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_ORGANIZATION_ID=your-openai-org-id-here
```

### Usage

```python
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Your prompt"}]
)
```

## Google Cloud Platform

### Setup

1. Create a project in Google Cloud Console
2. Enable required APIs
3. Create a service account and download credentials
4. Configure environment:

```env
GOOGLE_CLOUD_PROJECT_ID=your-google-project-id-here
GOOGLE_APPLICATION_CREDENTIALS=path-to-your-service-account-json
GOOGLE_API_KEY=your-google-api-key-here
```

## Figma Integration

### Setup

1. Generate a personal access token in Figma
2. Configure environment:

```env
FIGMA_ACCESS_TOKEN=your-figma-access-token-here
FIGMA_FILE_KEY=your-figma-file-key-here
```

### Usage

```python
import requests

headers = {
    'X-Figma-Token': os.environ["FIGMA_ACCESS_TOKEN"]
}
file_key = os.environ["FIGMA_FILE_KEY"]
response = requests.get(
    f'https://api.figma.com/v1/files/{file_key}',
    headers=headers
)
```

## HubSpot Integration

### Setup

1. Create a HubSpot account
2. Generate an API key or private app access token
3. Configure environment:

```env
HUBSPOT_API_KEY=your-hubspot-api-key-here
HUBSPOT_ACCESS_TOKEN=your-hubspot-access-token-here
HUBSPOT_PORTAL_ID=your-hubspot-portal-id-here
```

### Usage

```python
import requests

headers = {
    'Authorization': f'Bearer {os.environ["HUBSPOT_ACCESS_TOKEN"]}'
}
response = requests.get(
    'https://api.hubapi.com/crm/v3/objects/contacts',
    headers=headers
)
```

## Security Best Practices

1. **Never commit secrets**: Always use `.env` files and add them to `.gitignore`
2. **Rotate keys regularly**: Update API keys periodically
3. **Use minimal permissions**: Only grant necessary access levels
4. **Monitor usage**: Track API usage to detect anomalies
5. **Use environment-specific keys**: Separate keys for development, staging, and production

## Rate Limits

Each service has different rate limits:

- **Gemini**: Check current limits in Google AI Studio
- **OpenAI**: Varies by plan and model
- **Google Cloud**: Depends on service and quotas
- **Figma**: 1000 requests per minute
- **HubSpot**: 100 requests per 10 seconds

## Error Handling

Always implement proper error handling:

```python
import os
from typing import Optional

def safe_api_call(api_function):
    try:
        return api_function()
    except Exception as e:
        print(f"API Error: {e}")
        return None
```

## Testing

Use separate API keys for testing:

```bash
# .env.test
GEMINI_API_KEY=test-gemini-key
OPENAI_API_KEY=test-openai-key
# ... other test keys
```

## Additional Resources

- [Google Gemini Documentation](https://ai.google.dev/docs)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Figma API Documentation](https://www.figma.com/developers/api)
- [HubSpot API Documentation](https://developers.hubspot.com/)
