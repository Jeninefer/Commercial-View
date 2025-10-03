# Architecture Overview

## System Integration Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Commercial-View Platform                     │
│                  (Financial Dashboard & KPI)                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  AI Services │       │ Design Tools │       │   CRM & CI   │
└──────────────┘       └──────────────┘       └──────────────┘
        │                       │                       │
        │                       │                       │
   ┌────┴────┐             ┌───┴───┐            ┌──────┴──────┐
   │         │             │       │            │             │
   ▼         ▼             ▼       │            ▼             ▼
┌──────┐ ┌────────┐   ┌────────┐  │      ┌──────────┐  ┌──────────┐
│Gemini│ │OpenAI  │   │ Figma  │  │      │ HubSpot  │  │  GitHub  │
│  AI  │ │ GPT-4  │   │  API   │  │      │   CRM    │  │ Actions  │
└──────┘ └────────┘   └────────┘  │      └──────────┘  └──────────┘
                                   │
                              ┌────┴────┐
                              │ Google  │
                              │  Cloud  │
                              └─────────┘
```

## Integration Components

### 1. AI Services Layer

**Google Gemini**
- Advanced AI model access
- Natural language processing
- Content generation
- Environment: `GEMINI_API_KEY`, `GEMINI_PROJECT_ID`

**OpenAI GPT**
- GPT-4 model access
- Chat completions
- Code generation
- Environment: `OPENAI_API_KEY`, `OPENAI_ORGANIZATION_ID`

**Google Cloud Platform**
- Cloud AI services
- Machine learning APIs
- Infrastructure services
- Environment: `GOOGLE_CLOUD_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`

### 2. Design Tools Layer

**Figma**
- Design file access
- Asset retrieval
- Collaboration API
- Environment: `FIGMA_ACCESS_TOKEN`, `FIGMA_FILE_KEY`

### 3. CRM & CI/CD Layer

**HubSpot**
- Customer relationship management
- Marketing automation
- Contact management
- Environment: `HUBSPOT_API_KEY`, `HUBSPOT_ACCESS_TOKEN`

**GitHub Actions**
- Continuous integration
- Automated testing
- Deployment workflows
- Environment: `DEPLOY_VISUAL_CI_KEY`

## Data Flow

```
User Request
    │
    ▼
Commercial-View Platform
    │
    ├──► AI Services ──► Process & Generate Content
    │
    ├──► Design Tools ──► Fetch Design Assets
    │
    └──► CRM System ──► Update Customer Data
         │
         ▼
    Response to User
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          Environment Variables (.env)               │   │
│  │  - FIGMA_ACCESS_TOKEN                              │   │
│  │  - GEMINI_API_KEY                                  │   │
│  │  - OPENAI_API_KEY                                  │   │
│  │  - HUBSPOT_ACCESS_TOKEN                            │   │
│  │  - GOOGLE_APPLICATION_CREDENTIALS                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (encrypted at rest)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Secrets Management                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - GitHub Secrets (CI/CD)                          │   │
│  │  - Environment Variables (Local)                   │   │
│  │  - .gitignore (Exclusions)                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## CI/CD Pipeline

```
Developer Push
    │
    ▼
GitHub Actions Triggered
    │
    ├──► Setup SSH Environment
    │    └──► Use DEPLOY_VISUAL_CI_KEY
    │
    ├──► Clone Repository
    │
    ├──► Install Dependencies
    │    ├──► Python packages
    │    └──► Node modules
    │
    ├──► Run Tests
    │    ├──► Import smoke tests
    │    └──► Unit tests
    │
    └──► Code Quality Check
         └──► SonarQube Analysis
              └──► Use SONAR_TOKEN
```

## Quality Assurance Flow

```
Code Commit
    │
    ▼
SonarQube Scanner
    │
    ├──► Code Coverage Analysis
    │    ├──► Python: coverage.xml
    │    └──► JavaScript: lcov.info
    │
    ├──► Security Scanning
    │    ├──► Vulnerability detection
    │    └──► Secret detection
    │
    ├──► Code Quality Metrics
    │    ├──► Code smells
    │    ├──► Technical debt
    │    └──► Maintainability
    │
    └──► Quality Gate
         ├──► Pass ──► Deploy
         └──► Fail ──► Block
```

## Configuration Management

```
Repository Structure
│
├── .env.example ──────────► Template for developers
│   └──► Copy to .env for local development
│
├── .gitignore ────────────► Excludes sensitive files
│   └──► Ensures .env is never committed
│
├── sonar-project.properties ──► Quality configuration
│   └──► Used by SonarQube scanner
│
└── .github/workflows/ ────► CI/CD automation
    └──► ci-ssh-checkout.yml
         └──► Uses GitHub Secrets
```

## Environment Separation

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Development  │     │   Staging    │     │ Production   │
├──────────────┤     ├──────────────┤     ├──────────────┤
│ .env.local   │     │ .env.staging │     │ .env.prod    │
│              │     │              │     │              │
│ Test Keys    │────►│ Test Keys    │────►│ Live Keys    │
│              │     │              │     │              │
│ Lower Limits │     │ Normal Limits│     │ Full Limits  │
└──────────────┘     └──────────────┘     └──────────────┘
```

## API Rate Limiting Strategy

```
Request
    │
    ▼
Rate Limiter
    │
    ├──► Within Limits ──► Process Request
    │                      │
    │                      ▼
    │                  API Service
    │
    └──► Exceeded ──────► Queue/Retry
                          │
                          ▼
                      Backoff Strategy
```

## Monitoring & Logging

```
Application Events
    │
    ├──► API Calls Logged
    │    └──► Without sensitive data
    │
    ├──► Error Tracking
    │    └──► Exception monitoring
    │
    └──► Usage Metrics
         ├──► API quota tracking
         └──► Performance metrics
```

## Disaster Recovery

```
Secret Compromised
    │
    ▼
Incident Response
    │
    ├──► 1. Revoke immediately
    │
    ├──► 2. Generate new credentials
    │
    ├──► 3. Update all environments
    │
    ├──► 4. Notify stakeholders
    │
    └──► 5. Document incident
```

## Documentation Structure

```
docs/
│
├── integrations/
│   ├── ai-services.md ────► Complete AI integration guide
│   └── meta-business.md ──► Meta Business Suite guide
│
├── setup/
│   └── claude-code-setup.md ──► Development tools
│
└── api/
    └── openapi-plant-store.json ──► API specifications
```

## Quick Start Flow

```
1. Clone Repository
   git clone https://github.com/Jeninefer/Commercial-View.git

2. Setup Environment
   cp .env.example .env

3. Configure Secrets
   Edit .env with your API keys

4. Install Dependencies
   [Language-specific installation]

5. Run Application
   [Application-specific startup]

6. Verify Integration
   [Test each service connection]
```

## Support Resources

- **SECRETS.md**: Complete secrets management guide
- **README.md**: Project overview and setup
- **IMPLEMENTATION.md**: Implementation details
- **docs/**: Service-specific documentation
