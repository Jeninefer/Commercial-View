# Commercial-View Dashboard

Enterprise-grade portfolio analytics dashboard for Abaco Capital.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app) and provides a web interface for the Commercial-View API.

## Prerequisites

- Node.js 18+

- npm or yarn

- Commercial-View API running on http://localhost:8000

## Quick Start

```bash

# Install dependencies

npm install

# Start development server

npm start

# Open http://localhost:3000 in your browser

```text

## Available Scripts

### `npm start`

Runs the app in development mode.\
Opens [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

**Note**: Ensure the Commercial-View API is running on port 8000 before starting the dashboard.

### `npm test`

Launches the test runner in interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

### `npm run lint`

Runs ESLint to check code quality and style consistency.

### `npm run format`

Formats code using Prettier (if configured).

## Dashboard Features

- **Portfolio Overview**: Real-time portfolio metrics and KPIs

- **Risk Analytics**: Risk assessment and scoring visualizations

- **Data Export**: Download reports and analysis results

- **Interactive Charts**: Dynamic data visualization with filtering

- **Responsive Design**: Works on desktop, tablet, and mobile devices

## API Integration

The dashboard connects to the Commercial-View FastAPI backend:

- **API Base URL**: http://localhost:8000

- **Health Check**: GET /health

- **Portfolio Data**: GET /executive-summary

- **Documentation**: http://localhost:8000/docs

## Environment Configuration

Create a `.env` file in this directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

```text

For production:

```env
REACT_APP_API_BASE_URL=https://your-api-domain.com
REACT_APP_ENVIRONMENT=production

```text

### Additional Environment Variables

For local development, you may also set up a `.env.local` file with the following content:

```dotenv
DATABASE_URL=postgresql://localhost/mydb
API_KEY=your-api-key-here
DEBUG=True

```text

## Testing

### Local Testing

```bash

# Run test suite

npm test

# Run tests with coverage

npm test -- --coverage

# Run tests in CI mode (single run)

npm test -- --ci --coverage --watchAll=false

```text

### Backend Integration Testing

Ensure the Commercial-View API is running before testing API integrations:

```bash

# Start the backend API first

cd ..  # Navigate to project root
python server_control.py --port 8000

# Then run frontend tests

cd frontend/dashboard
npm test

```text

⚠️ **Note**: `pytest -q` (backend tests) should not be run in read-only QA environments. Use dedicated development or testing environments for full test suite execution.

## Google Colab Integration

For cloud development and testing:

### Setup in Colab

```python

# Install Node.js in Colab

!curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
!sudo apt-get install -y nodejs

# Clone and setup

!git clone https://github.com/Jeninefer/Commercial-View.git
%cd Commercial-View/frontend/dashboard
!npm install

```text

### Development in Colab

```python

# Start development server (background process)

import subprocess
import time

# Start the React development server

react_server = subprocess.Popen(['npm', 'start'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
time.sleep(10)  # Wait for startup

# Use ngrok or Colab's built-in tunneling to expose port 3000

print("Dashboard server starting on port 3000")
print("Use Colab's port forwarding or ngrok for external access")

```text

### Export and Persistence

```python

# Build production assets

!npm run build

# Export build artifacts

!zip -r dashboard-build.zip build/

# Download or save to Google Drive

from google.colab import files
files.download('dashboard-build.zip')

```text

### Cleanup (Important for Colab)

```python

# Terminate long-running servers to avoid idle sessions

try:
    react_server.terminate()
    print("React server stopped")
except:
    print("Server was not running")

```text

## Project Structure

```text
/public
  /favicon.ico
  /index.html
/src
  /api
  /assets
  /components
  /hooks
  /pages
  /styles
  /utils
  App.js
  index.js
.gitignore
package.json
README.md

```text

## Development Workflow

### With Commercial-View Backend

1. **Start Backend**: Use `python server_control.py` in project root

2. **Start Frontend**: Run `npm start` in this directory

3. **Development**: Make changes with hot-reload enabled

4. **Testing**: Run `npm test` for frontend, coordinate with backend team for integration tests

5. **Export**: Use `abaco_runtime/exports/` integration for data persistence

### Data Export Integration

The dashboard integrates with the Commercial-View export system:

- **Export Location**: `../../abaco_runtime/exports/`

- **Google Drive Sync**: Uses `scripts/upload_to_drive.py`

- **Manual Export**: Download artifacts directly from dashboard UI

### Persist Outputs

Export artifacts from:

- `abaco_runtime/exports/` (backend generated)

- `build/` (frontend production build)

- `coverage/` (test coverage reports)

Save to Google Drive or download manually when finished with development sessions.

This comprehensive README includes:

1. **Complete setup instructions** for local and cloud development

2. **API integration details** with the Commercial-View backend

3. **Google Colab support** for cloud development

4. **Testing guidance** with environment considerations

5. **Deployment options** including Docker

6. **Troubleshooting section** with common issues and solutions

7. **Integration context** within the larger Commercial-View ecosystem

8. **Development workflow** that aligns with the project structure

The documentation provides developers with everything they need to work with the Commercial-View dashboard effectively.
