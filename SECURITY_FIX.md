# Security Fix Guide

## Problem

GitHub is blocking your push because `.env` file with secrets was committed in `bb4eb8aa9bf369f0f028167292907736bb206c84`.

## Solution Options

### Option 1: Use the automated script (Recommended)

```bash
chmod +x fix_secrets_and_push.sh
./fix_secrets_and_push.sh
git push origin main --force
```

### Option 2: Manual fix (if script fails)

```bash
# 1. Install BFG Repo Cleaner (faster alternative)
brew install bfg  # macOS
# or download from https://rtyley.github.io/bfg-repo-cleaner/

# 2. Remove .env from history
bfg --delete-files .env

# 3. Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push
git push origin main --force
```

### Option 3: GitHub's allow links (Quick but not secure)

Visit these URLs to temporarily allow the secrets (NOT RECOMMENDED):

- OpenAI: https://github.com/Jeninefer/Commercial-View/security/secret-scanning/unblock-secret/33pPbaktO1pP5MHEswQVvZlD8aL
- Slack: https://github.com/Jeninefer/Commercial-View/security/secret-scanning/unblock-secret/33pPbbHG3gXMVPi0be3SIfWWyqQ
- Figma: https://github.com/Jeninefer/Commercial-View/security/secret-scanning/unblock-secret/33pPbb4XPIQZ07AW8eqotXxsBMw

Then push again. **After pushing, immediately rotate all secrets.**

### Option 4: Start fresh (Nuclear option)

If nothing else works:

```bash
# 1. Create a new branch without the problematic commit
git checkout -b main-clean $(git rev-list --max-parents=0 HEAD)

# 2. Cherry-pick all good commits (skip the one with .env)
git cherry-pick <commit1> <commit2> ... # Skip bb4eb8aa9bf369f0f028167292907736bb206c84

# 3. Force push
git push origin main-clean:main --force
```

## After Successful Push

### IMMEDIATELY Rotate These Secrets:

1. **OpenAI API Key**

   - Go to: https://platform.openai.com/api-keys
   - Revoke old key
   - Create new key
   - Update `.env` file

2. **Slack API Token**

   - Go to: https://api.slack.com/apps
   - Find your app
   - Regenerate OAuth token
   - Update `.env` file

3. **Figma Access Token**
   - Go to: https://www.figma.com/developers/api#access-tokens
   - Revoke old token
   - Generate new token
   - Update `.env` file

### Verify Security

```bash
# Check that .env is not tracked
git ls-files | grep .env
# Should return nothing

# Check .env is in .gitignore
grep .env .gitignore
# Should show .env entries

# Verify no secrets in recent commits
git log --all --full-history --source --pretty=format:"%H" -- .env
# Should return empty or old commits only
```

## Prevention

1. Always use `.env.example` for templates
2. Never commit `.env` files
3. Use environment variables in production
4. Enable GitHub secret scanning
5. Use pre-commit hooks to catch secrets

## Support

If you need help, contact the security team immediately.
