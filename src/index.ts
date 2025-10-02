import * as path from 'path';
import { calculateAllKPIs, calcProgress, KPIData, Q4Targets } from './kpiCalculations';

/**
 * Q4 Targets - These can be configured or loaded from a separate configuration file
 */
const q4Targets: Q4Targets = {
  outstandingPortfolio: 700000,
  weightedAPR: 8.5,
  tenorMix: {
    '0-12': 0.15,    // 15% target for short-term loans
    '13-24': 0.40,   // 40% target for medium-term loans
    '25-36': 0.35,   // 35% target for long-term loans
    '37+': 0.10      // 10% target for extended loans
  },
  concentration: 25,  // Top customer should not exceed 25% of portfolio
  npl: 5,            // NPL target: less than 5%
  dpd: 3,            // Average DPD target: less than 3 days
  clientGoals: {
    totalClients: 20,
    newClients: 10,
    recurringClients: 5,
    recoveredClients: 3
  }
};

/**
 * Generate KPI report with progress tracking
 */
export function generateKPIReport(dataDir: string): {
  kpis: KPIData;
  targets: Q4Targets;
  progress: {
    [key: string]: number;
  };
} {
  const kpis = calculateAllKPIs(dataDir);
  
  // Calculate progress for each KPI
  const progress = {
    outstandingPortfolio: calcProgress(kpis.outstandingPortfolio, q4Targets.outstandingPortfolio),
    weightedAPR: calcProgress(kpis.weightedAPR, q4Targets.weightedAPR),
    nplPercentage: calcProgress(kpis.npl.percentage, q4Targets.npl),
    averageDPD: calcProgress(kpis.dpd.averageDPD, q4Targets.dpd),
    totalClients: calcProgress(kpis.clientGoals.totalClients, q4Targets.clientGoals.totalClients),
    newClients: calcProgress(kpis.clientGoals.newClients, q4Targets.clientGoals.newClients),
    recurringClients: calcProgress(kpis.clientGoals.recurringClients, q4Targets.clientGoals.recurringClients),
    recoveredClients: calcProgress(kpis.clientGoals.recoveredClients, q4Targets.clientGoals.recoveredClients)
  };
  
  return {
    kpis,
    targets: q4Targets,
    progress
  };
}

/**
 * Display KPI report in console
 */
export function displayKPIReport(dataDir: string): void {
  const report = generateKPIReport(dataDir);
  
  console.log('\n=== COMMERCIAL VIEW - KPI DASHBOARD ===\n');
  
  console.log('📊 OUTSTANDING PORTFOLIO');
  console.log(`   Current: $${report.kpis.outstandingPortfolio.toLocaleString()}`);
  console.log(`   Target:  $${report.targets.outstandingPortfolio.toLocaleString()}`);
  console.log(`   Progress: ${report.progress.outstandingPortfolio}%\n`);
  
  console.log('💹 WEIGHTED APR');
  console.log(`   Current: ${report.kpis.weightedAPR.toFixed(2)}%`);
  console.log(`   Target:  ${report.targets.weightedAPR}%`);
  console.log(`   Progress: ${report.progress.weightedAPR}%\n`);
  
  console.log('📅 TENOR MIX');
  Object.entries(report.kpis.tenorMix).forEach(([bucket, balance]) => {
    const percentage = report.kpis.outstandingPortfolio > 0 
      ? (balance / report.kpis.outstandingPortfolio * 100).toFixed(1)
      : '0.0';
    console.log(`   ${bucket} months: $${balance.toLocaleString()} (${percentage}%)`);
  });
  console.log();
  
  console.log('🎯 CONCENTRATION');
  console.log(`   Top 5 Customers:`);
  report.kpis.concentration.topCustomers.slice(0, 5).forEach((customer, index) => {
    console.log(`   ${index + 1}. ${customer.customerId}: $${customer.balance.toLocaleString()} (${customer.percentage.toFixed(2)}%)`);
  });
  console.log();
  
  console.log('⚠️  NPL (Non-Performing Loans)');
  console.log(`   Count: ${report.kpis.npl.count}`);
  console.log(`   Percentage: ${report.kpis.npl.percentage.toFixed(2)}%`);
  console.log(`   Target: < ${report.targets.npl}%`);
  console.log(`   Progress: ${report.progress.nplPercentage}%\n`);
  
  console.log('⏰ DPD (Days Past Due)');
  console.log(`   Current payments: ${report.kpis.dpd.current}`);
  console.log(`   Late payments: ${report.kpis.dpd.late}`);
  console.log(`   Average DPD: ${report.kpis.dpd.averageDPD.toFixed(2)} days`);
  console.log(`   Target: < ${report.targets.dpd} days`);
  console.log(`   Progress: ${report.progress.averageDPD}%\n`);
  
  console.log('👥 CLIENT GOALS');
  console.log(`   Total Clients: ${report.kpis.clientGoals.totalClients} (Target: ${report.targets.clientGoals.totalClients}, Progress: ${report.progress.totalClients}%)`);
  console.log(`   New Clients: ${report.kpis.clientGoals.newClients} (Target: ${report.targets.clientGoals.newClients}, Progress: ${report.progress.newClients}%)`);
  console.log(`   Recurring: ${report.kpis.clientGoals.recurringClients} (Target: ${report.targets.clientGoals.recurringClients}, Progress: ${report.progress.recurringClients}%)`);
  console.log(`   Recovered: ${report.kpis.clientGoals.recoveredClients} (Target: ${report.targets.clientGoals.recoveredClients}, Progress: ${report.progress.recoveredClients}%)`);
  console.log('\n=====================================\n');
}

// Main execution
if (require.main === module) {
  const dataDir = path.join(__dirname, '..', 'data');
  displayKPIReport(dataDir);
}
