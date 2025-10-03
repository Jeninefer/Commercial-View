# Google Drive Authentication Guide

## Overview

The Commercial View Platform uses OAuth 2.0 to securely access Google Drive and Google Sheets. This guide walks you through the complete authentication setup process.

## Prerequisites

- Google Account with access to the target Drive folder
- Google Cloud Project (or ability to create one)
- Python environment with project dependencies installed

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "New Project"
3. Enter project name: "Commercial View" (or similar)
4. Click "Create"

### 2. Enable Required APIs

1. Navigate to "APIs & Services" → "Library"
2. Search for and enable:
   - **Google Drive API**
   - **Google Sheets API**

### 3. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: Internal (if available) or External
   - App name: "Commercial View"
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: Add Drive and Sheets read-only scopes
4. Application type: **Desktop app**
5. Name: "Commercial View Desktop"
6. Click "Create"

### 4. Download Credentials

1. Click the download icon next to your OAuth client
2. Save the file as `credentials.json`
3. Move it to your project root directory:
   ```
   Commercial-View/
   ├── credentials.json  ← Place here
   ├── config/
   ├── dashboard/
   └── ...
   ```

### 5. First-Time Authentication

Run the authentication flow:

```bash
python -c "from ingestion import GoogleDriveClient; client = GoogleDriveClient(); client.authenticate()"
```

This will:
1. Open a browser window
2. Ask you to select your Google account
3. Show permission request for Drive and Sheets access
4. Save authentication token to `token.json`

**Important**: The browser might show "Google hasn't verified this app" warning. Click "Advanced" → "Go to Commercial View (unsafe)" to proceed.

### 6. Verify Authentication

Test that authentication works:

```python
from ingestion import GoogleDriveClient

client = GoogleDriveClient()
client.authenticate()

# Test listing files
files = client.list_files('your-folder-id')
print(f"Found {len(files)} files")
```

## Troubleshooting

### Error: "credentials.json not found"

**Solution**: Ensure credentials.json is in the project root directory, not in a subdirectory.

### Error: "Access blocked: This app's request is invalid"

**Solution**: 
1. Check OAuth consent screen configuration
2. Add your email as a test user (for External apps)
3. Ensure correct scopes are added

### Error: "invalid_grant" or Token Expired

**Solution**: Delete `token.json` and re-authenticate:
```bash
rm token.json
python -c "from ingestion import GoogleDriveClient; client = GoogleDriveClient(); client.authenticate()"
```

### Browser Doesn't Open

**Solution**: The authentication URL will be printed to console. Copy and paste it into your browser manually.

## Security Best Practices

1. **Never commit credentials.json or token.json** to version control
   - These files are already in `.gitignore`
   
2. **Rotate credentials periodically**
   - Regenerate OAuth client every 90 days
   
3. **Use minimal scopes**
   - Read-only access where possible
   - Avoid full Drive access if not needed

4. **Service Account Alternative**
   For production deployments, consider using a service account:
   ```python
   from google.oauth2 import service_account
   
   credentials = service_account.Credentials.from_service_account_file(
       'service-account-key.json',
       scopes=['https://www.googleapis.com/auth/drive.readonly']
   )
   ```

## Sharing Access with Multiple Users

For team deployments:

### Option 1: Shared Service Account (Recommended)
1. Create service account in Google Cloud Console
2. Download key as JSON
3. Share the service account key securely
4. Grant service account access to Drive folder

### Option 2: Individual OAuth
- Each user authenticates with their own Google account
- Requires each user to have access to the Drive folder
- More secure but less convenient

## Production Considerations

### Token Storage
- Store `token.json` securely (encrypted storage, secrets manager)
- Never expose tokens in logs or error messages
- Implement token rotation policy

### Error Handling
```python
from google.auth.exceptions import RefreshError

try:
    client = GoogleDriveClient()
    client.authenticate()
except RefreshError:
    # Token expired, re-authenticate
    os.remove('token.json')
    client.authenticate()
```

### Monitoring
- Set up alerts for authentication failures
- Monitor API quota usage
- Log all Drive API calls for audit trail

## Additional Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/guides/about-sdk)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api/guides/concepts)
