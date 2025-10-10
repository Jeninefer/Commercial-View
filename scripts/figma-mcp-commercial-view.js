
const express = require('express');
const cors = require('cors');
const { createServer } = require('http');
const { Server } = require('socket.io');

const app = express();
const server = createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

app.use(cors());
app.use(express.json());

const FIGMA_TOKEN = process.env.FIGMA_PERSONAL_ACCESS_TOKEN;
const CONFIG = {
  "figma": {
    "api_base_url": "https://api.figma.com/v1",
    "commercial_view": {
      "dashboard_file_id": "Zli1oqL-_I1usmRAkOZtRTXdTWeHF6E-OTKKhgJwKPE",
      "components": {
        "kpi_tiles": true,
        "charts": true,
        "tables": true,
        "navigation": true,
        "pricing_matrix": true,
        "risk_indicators": true
      },
      "commercial_lending": {
        "loan_dashboards": [],
        "portfolio_views": [],
        "regulatory_reports": []
      }
    },
    "rate_limits": {
      "requests_per_minute": 60,
      "burst_limit": 10
    },
    "cache": {
      "enabled": true,
      "ttl_seconds": 300
    }
  }
};

// Rate limiting setup
const rateLimit = new Map();
const checkRateLimit = (req, res, next) => {
    const ip = req.ip;
    const now = Date.now();
    const windowMs = 60000; // 1 minute
    const limit = CONFIG.figma.rate_limits.requests_per_minute;

    if (!rateLimit.has(ip)) {
        rateLimit.set(ip, { count: 1, resetTime: now + windowMs });
        return next();
    }

    const userLimit = rateLimit.get(ip);
    if (now > userLimit.resetTime) {
        userLimit.count = 1;
        userLimit.resetTime = now + windowMs;
        return next();
    }

    if (userLimit.count >= limit) {
        return res.status(429).json({ error: 'Rate limit exceeded' });
    }

    userLimit.count++;
    next();
};

// Apply rate limiting to Figma API routes
app.use('/figma', checkRateLimit);
app.use('/commercial-view', checkRateLimit);

// Enhanced health endpoint
app.get('/health', (req, res) => {
    const healthStatus = {
        status: 'healthy',
        service: 'Commercial-View Figma MCP',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
        token_status: FIGMA_TOKEN ? 'configured' : 'missing',
        config: {
            dashboard_id: CONFIG.figma.commercial_view.dashboard_file_id ? 'configured' : 'missing',
            components_enabled: Object.keys(CONFIG.figma.commercial_view.components).filter(
                key => CONFIG.figma.commercial_view.components[key]
            ).length,
            rate_limit: CONFIG.figma.rate_limits.requests_per_minute,
            cache_enabled: CONFIG.figma.cache.enabled
        }
    };
    res.json(healthStatus);
});

app.get('/figma/me', async (req, res) => {
    try {
        const fetch = await import('node-fetch');
        const response = await fetch.default('https://api.figma.com/v1/me', {
            headers: {
                'X-Figma-Token': FIGMA_TOKEN
            }
        });
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error fetching user info:', error);
        res.status(500).json({ error: error.message });
    }
});

// Commercial-View specific endpoints
app.get('/commercial-view/dashboard', async (req, res) => {
    try {
        const dashboardId = CONFIG.figma.commercial_view.dashboard_file_id;
        if (!dashboardId) {
            return res.status(404).json({ error: 'Dashboard file ID not configured' });
        }

        const fetch = await import('node-fetch');
        const response = await fetch.default(`https://api.figma.com/v1/files/${dashboardId}`, {
            headers: {
                'X-Figma-Token': FIGMA_TOKEN
            }
        });
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error fetching dashboard:', error);
        res.status(500).json({ error: error.message });
    }
});

const port = process.env.PORT || 3001;
server.listen(port, () => {
    console.log(`🏦 Commercial-View Figma MCP server running on port ${port}`);
    console.log(`🎨 Dashboard ID: ${CONFIG.figma.commercial_view.dashboard_file_id}`);
    console.log(`🔑 Token: ${FIGMA_TOKEN ? FIGMA_TOKEN.substring(0, 10) + '...' : 'Not set'}`);
    console.log(`📊 Available endpoints:`);
    console.log(`   GET  /health`);
    console.log(`   GET  /figma/me`);
    console.log(`   GET  /commercial-view/dashboard`);
    console.log(`🚀 Commercial lending features enabled`);
});
