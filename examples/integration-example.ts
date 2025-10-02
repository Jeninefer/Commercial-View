/**
 * Integration Example: Connecting External Systems
 * Demonstrates how to integrate with APIs, repositories, and other data sources
 */

import {
  IntegrationManager,
  APIIntegration,
  RepositoryIntegration,
  CommercialViewEngine,
  DashboardConfig,
  KPIMetric,
  TimePeriod,
  KPIStatus,
  TrendDirection
} from '../src/index';

// Initialize components
const engine = new CommercialViewEngine();
const integrationManager = new IntegrationManager();

async function demonstrateIntegrations(): Promise<void> {
  console.log('=== Commercial View - Integration Example ===\n');

  // 1. API Integration
  console.log('1. API INTEGRATION');
  console.log('-------------------');
  
  const salesAPIIntegration = new APIIntegration(
    'https://api.example.com/sales',
    'demo-api-key-12345'
  );

  integrationManager.registerIntegration(
    {
      id: 'sales-api',
      name: 'Sales Analytics API',
      type: 'api',
      enabled: true,
      endpoint: 'https://api.example.com/sales',
      apiKey: 'demo-api-key-12345',
      settings: {
        timeout: 30000,
        retries: 3
      }
    },
    salesAPIIntegration
  );

  console.log('✓ Registered Sales Analytics API integration');
  
  try {
    const connected = await integrationManager.connect('sales-api');
    console.log(`✓ Connection status: ${connected ? 'Connected' : 'Failed'}`);
    
    // Simulate fetching data
    const apiData = await integrationManager.fetchData('sales-api', {
      period: 'daily',
      metrics: ['revenue', 'transactions']
    });
    console.log(`✓ Fetched ${apiData.length} data points from API`);
  } catch (error) {
    console.log(`⚠ Integration error: ${(error as Error).message}`);
  }

  // 2. Repository Integration
  console.log('\n\n2. REPOSITORY INTEGRATION');
  console.log('--------------------------');
  
  const githubIntegration = new RepositoryIntegration(
    'https://github.com/Jeninefer/Commercial-View',
    'github-token-placeholder'
  );

  integrationManager.registerIntegration(
    {
      id: 'github-repo',
      name: 'GitHub Repository Metrics',
      type: 'repository',
      enabled: true,
      settings: {
        trackMetrics: ['commits', 'pullRequests', 'issues', 'contributors']
      }
    },
    githubIntegration
  );

  console.log('✓ Registered GitHub repository integration');
  
  try {
    const repoConnected = await integrationManager.connect('github-repo');
    console.log(`✓ Connection status: ${repoConnected ? 'Connected' : 'Failed'}`);
    
    const repoData = await integrationManager.fetchData('github-repo', {
      since: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) // Last 7 days
    });
    console.log(`✓ Fetched ${repoData.length} repository metrics`);
  } catch (error) {
    console.log(`⚠ Integration error: ${(error as Error).message}`);
  }

  // 3. Multiple Integration Dashboard
  console.log('\n\n3. MULTI-SOURCE DASHBOARD');
  console.log('--------------------------');
  
  const integratedDashboard: DashboardConfig = {
    id: 'integrated-dashboard',
    name: 'Multi-Source Analytics Dashboard',
    description: 'Combines data from multiple external sources',
    metrics: [
      {
        id: 'api-revenue',
        name: 'API Revenue Stream',
        description: 'Revenue data from external API',
        category: 'Financial',
        unit: 'USD',
        currentValue: 0,
        targetValue: 100000,
        threshold: {
          excellent: 100000,
          good: 80000,
          warning: 60000,
          critical: 40000
        },
        trend: {
          direction: TrendDirection.STABLE,
          percentage: 0,
          comparisonPeriod: TimePeriod.DAILY
        },
        historicalData: [],
        status: KPIStatus.UNKNOWN,
        tags: ['api', 'external', 'revenue']
      },
      {
        id: 'repo-activity',
        name: 'Repository Activity Score',
        description: 'Development activity from GitHub',
        category: 'Development',
        unit: 'score',
        currentValue: 0,
        targetValue: 100,
        threshold: {
          excellent: 100,
          good: 75,
          warning: 50,
          critical: 25
        },
        trend: {
          direction: TrendDirection.STABLE,
          percentage: 0,
          comparisonPeriod: TimePeriod.WEEKLY
        },
        historicalData: [],
        status: KPIStatus.UNKNOWN,
        tags: ['development', 'repository', 'activity']
      }
    ],
    refreshInterval: 300000 // 5 minutes
  };

  engine.registerDashboard(integratedDashboard);
  console.log(`✓ Created dashboard: ${integratedDashboard.name}`);
  console.log(`  - Metrics: ${integratedDashboard.metrics.length}`);
  console.log(`  - Data sources: ${integrationManager.getIntegrations().length}`);

  // 4. List All Integrations
  console.log('\n\n4. INTEGRATION SUMMARY');
  console.log('-----------------------');
  
  const allIntegrations = integrationManager.getIntegrations();
  console.log(`\nTotal integrations: ${allIntegrations.length}\n`);
  
  allIntegrations.forEach(integration => {
    const isConnected = integrationManager.isIntegrationConnected(integration.id);
    const status = isConnected ? '✓' : '○';
    console.log(`  ${status} ${integration.name}`);
    console.log(`    Type: ${integration.type}`);
    console.log(`    Status: ${integration.enabled ? 'Enabled' : 'Disabled'}`);
    console.log(`    Connected: ${isConnected ? 'Yes' : 'No'}`);
    console.log('');
  });

  // 5. Integration Best Practices
  console.log('5. INTEGRATION BEST PRACTICES');
  console.log('-------------------------------');
  console.log('\n✓ Always validate connection before fetching data');
  console.log('✓ Implement proper error handling and retries');
  console.log('✓ Use appropriate refresh intervals to avoid rate limits');
  console.log('✓ Cache data when possible to reduce API calls');
  console.log('✓ Monitor integration health and performance');
  console.log('✓ Secure API keys and credentials properly');
  console.log('✓ Log integration activities for debugging');
  console.log('✓ Implement fallback mechanisms for critical data\n');
}

// Run the integration demonstration
demonstrateIntegrations().catch(error => {
  console.error('Error in integration demonstration:', error);
});

export { integrationManager, engine };
