# Claude Code Setup

Configure Claude Code for your documentation workflow.

## Prerequisites

- Active Claude subscription (Pro, Max, or API access)

## Setup

1. Install Claude Code globally:

   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. Navigate to your docs directory.
3. (Optional) Add the `CLAUDE.md` file below to your project.
4. **Configure your API key securely** (see Security section below).
5. Run `claude` to start.

## Create `CLAUDE.md`

Create a `CLAUDE.md` file at the root of your documentation repository to train Claude Code on your specific documentation standards.

## Security Best Practices

### API Key Management

**Never include API keys directly in your code.** Instead, use environment variables:

```bash
# Set your Claude API key as an environment variable
export ANTHROPIC_API_KEY="your-api-key-here"
```

For persistent configuration, add to your shell profile:

```bash
# In ~/.bashrc, ~/.zshrc, or similar
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Development vs Production

Create separate configuration files for different environments:

```javascript
// config/development.js
module.exports = {
  apiKey: process.env.ANTHROPIC_API_KEY,
  endpoint: process.env.ANTHROPIC_ENDPOINT || "https://api.anthropic.com",
};
```

### .gitignore Setup

Always exclude sensitive files from version control:

```gitignore
# Environment variables
.env
.env.local
.env.production

# API keys and secrets
config/secrets.json
*.key
*.pem
```

## Git Commands Reference

### Essential Commands

```bash
# Check current status
git status

# View commit history
git log --oneline -10

# Create and switch to new branch
git checkout -b feature/new-feature

# Stage all changes
git add .

# Commit with message
git commit -m "type: description"

# Push to remote
git push origin branch-name

# Pull latest changes
git pull origin main

# Merge main into current branch
git merge main

# Stash changes temporarily
git stash
git stash pop
```

### Commit Message Format

Use conventional commit format:

```bash
# Format: type(scope): description

git commit -m "feat: add new documentation section"
git commit -m "fix: correct typo in setup guide"
git commit -m "docs: update API examples"
git commit -m "style: format code blocks"
git commit -m "refactor: reorganize file structure"
git commit -m "test: add unit tests"
git commit -m "chore: update dependencies"
```

## Troubleshooting

### Common Issues

**API Key Not Found**

```bash
# Verify environment variable is set
echo $ANTHROPIC_API_KEY

# Re-export if needed
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Permission Denied**

```bash
# Check file permissions
ls -la

# Make script executable if needed
chmod +x script.sh
```

**Merge Conflicts**

```bash
# Abort merge if needed
git merge --abort

# Reset to previous state
git reset --hard HEAD~1
```
