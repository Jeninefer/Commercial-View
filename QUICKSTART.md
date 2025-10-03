# Quick Start Guide

Get up and running with Commercial-View in 5 minutes.

## Prerequisites

- Git installed
- Python 3.9+ or Node.js (depending on your project stack)
- GitHub account with access to the repository

## Step 1: Clone the Repository

```bash
git clone https://github.com/Jeninefer/Commercial-View.git
cd Commercial-View
```

## Step 2: Setup Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

## Step 3: Configure Your API Keys

Open `.env` in your text editor and add your API keys:

```env
# Figma - Get from https://www.figma.com/developers/api
FIGMA_ACCESS_TOKEN=your-actual-figma-token
FIGMA_FILE_KEY=your-actual-file-key

# Google Gemini - Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-actual-gemini-key
GEMINI_PROJECT_ID=your-actual-project-id

# Google Cloud - Get from https://console.cloud.google.com
GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_API_KEY=your-actual-api-key

# OpenAI - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=your-actual-openai-key
OPENAI_ORGANIZATION_ID=your-actual-org-id

# HubSpot - Get from HubSpot Settings > Integrations
HUBSPOT_API_KEY=your-actual-hubspot-key
HUBSPOT_ACCESS_TOKEN=your-actual-access-token
HUBSPOT_PORTAL_ID=your-actual-portal-id
```

## Step 4: Install Dependencies

### For Python Projects:
```bash
pip install -r requirements.txt
```

### For Node.js Projects:
```bash
npm install
```

## Step 5: Verify Installation

Test that your environment is configured correctly:

### Python:
```bash
python -c "import os; print('✅ Gemini:', 'OK' if os.getenv('GEMINI_API_KEY') else 'MISSING')"
python -c "import os; print('✅ OpenAI:', 'OK' if os.getenv('OPENAI_API_KEY') else 'MISSING')"
python -c "import os; print('✅ Figma:', 'OK' if os.getenv('FIGMA_ACCESS_TOKEN') else 'MISSING')"
```

### Node.js:
```bash
node -e "console.log('✅ Gemini:', process.env.GEMINI_API_KEY ? 'OK' : 'MISSING')"
node -e "console.log('✅ OpenAI:', process.env.OPENAI_API_KEY ? 'OK' : 'MISSING')"
node -e "console.log('✅ Figma:', process.env.FIGMA_ACCESS_TOKEN ? 'OK' : 'MISSING')"
```

## Step 6: Start Development

You're ready to go! 🎉

## Common Tasks

### View Documentation
```bash
# Open docs in your browser
open docs/integrations/ai-services.md
open docs/setup/claude-code-setup.md
```

### Test a Specific Integration

#### Test Gemini:
```python
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello, world!")
print(response.text)
```

#### Test OpenAI:
```python
import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

#### Test Figma:
```python
import requests
import os

headers = {'X-Figma-Token': os.environ["FIGMA_ACCESS_TOKEN"]}
file_key = os.environ["FIGMA_FILE_KEY"]
response = requests.get(f'https://api.figma.com/v1/files/{file_key}', headers=headers)
print(response.status_code)
```

### Run Tests
```bash
# Python
python -m pytest

# Or unittest
python -m unittest discover tests/

# Node.js
npm test
```

### Run Code Quality Check
```bash
sonar-scanner
```

## Troubleshooting

### "Module not found" error
```bash
# Python: Reinstall dependencies
pip install --upgrade -r requirements.txt

# Node.js: Reinstall dependencies
npm install
```

### "API key not found" error
```bash
# Check if .env file exists
ls -la .env

# Verify environment variables are loaded
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"

# If empty, make sure you saved the .env file
```

### "Permission denied" error
```bash
# Make sure .env has proper permissions
chmod 600 .env

# Or for the whole project
chmod -R u+rw .
```

### "Rate limit exceeded" error
- Check API usage in your service dashboard
- Implement rate limiting in your code
- Use caching to reduce API calls

## Next Steps

1. **Read the documentation**: Check out `docs/` for detailed guides
2. **Review secrets management**: See `SECRETS.md` for security best practices
3. **Understand the architecture**: Read `ARCHITECTURE.md` for system overview
4. **Configure CI/CD**: Set up GitHub secrets for automated testing

## Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Create an issue on GitHub
- **Security**: See `SECRETS.md` for security questions

## Security Reminders

⚠️ **Important**: 
- Never commit your `.env` file
- Never share API keys in chat or email
- Rotate keys regularly
- Use separate keys for development and production

## Useful Links

- [Figma API Docs](https://www.figma.com/developers/api)
- [Google Gemini Docs](https://ai.google.dev/docs)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [HubSpot API Docs](https://developers.hubspot.com/)
- [Google Cloud Docs](https://cloud.google.com/docs)

---

**You're all set!** Happy coding! 🚀
