import * as path from 'path';
import {
  calcProgress,
  calculateOutstandingPortfolio,
  calculateWeightedAPR,
  calculateTenorMix,
  calculateConcentration,
  calculateNPL,
  calculateDPD,
  calculateClientGoals,
  calculateAllKPIs
} from '../src/kpiCalculations';

const dataDir = path.join(__dirname, '..', 'data');

function assert(condition: boolean, message: string) {
  if (!condition) {
    console.error(`❌ FAILED: ${message}`);
    process.exit(1);
  }
  console.log(`✅ PASSED: ${message}`);
}

function assertApprox(actual: number, expected: number, tolerance: number, message: string) {
  const diff = Math.abs(actual - expected);
  if (diff > tolerance) {
    console.error(`❌ FAILED: ${message}`);
    console.error(`   Expected: ${expected}, Actual: ${actual}, Diff: ${diff}`);
    process.exit(1);
  }
  console.log(`✅ PASSED: ${message}`);
}

console.log('\n=== Running KPI Calculation Tests ===\n');

// Test calcProgress function
console.log('Testing calcProgress function...');
assert(calcProgress(50, 100) === 50, 'calcProgress(50, 100) should return 50');
assert(calcProgress(75, 100) === 75, 'calcProgress(75, 100) should return 75');
assert(calcProgress(100, 100) === 100, 'calcProgress(100, 100) should return 100');
assert(calcProgress(150, 100) === 150, 'calcProgress(150, 100) should return 150');
assert(calcProgress(0, 100) === 0, 'calcProgress(0, 100) should return 0');
assert(calcProgress(100, 0) === 0, 'calcProgress(100, 0) should return 0 (avoid division by zero)');
console.log();

// Test Outstanding Portfolio
console.log('Testing Outstanding Portfolio calculation...');
const portfolio = calculateOutstandingPortfolio(dataDir);
console.log(`   Portfolio value: $${portfolio.toLocaleString()}`);
assert(portfolio > 0, 'Portfolio should be greater than 0');
// Sum of latest balances: CUST001(95000) + CUST002(48000) + CUST003(200000) + CUST004(75000) + CUST005(120000) = 538000
assertApprox(portfolio, 538000, 1000, 'Portfolio should be approximately $538,000');
console.log();

// Test Weighted APR
console.log('Testing Weighted APR calculation...');
const weightedAPR = calculateWeightedAPR(dataDir);
console.log(`   Weighted APR: ${weightedAPR.toFixed(2)}%`);
assert(weightedAPR > 0, 'Weighted APR should be greater than 0');
// Dynamically calculate expected weighted APR from the same data used in the test to avoid brittleness.
const fs = require('fs');
const parse = require('csv-parse/sync').parse;
const csvData = fs.readFileSync(path.join(dataDir, 'loan_data.csv'), 'utf8');
const loans = parse(csvData, { columns: true });
let totalWeightedAPR = 0;
let totalBalance = 0;
for (const loan of loans) {
  // CSV fields are strings; convert to numbers
  const balance = Number(loan.balance);
  const apr = Number(loan.apr);
  if (!isNaN(balance) && !isNaN(apr)) {
    totalWeightedAPR += balance * apr;
    totalBalance += balance;
  }
}
const expectedWeightedAPR = totalBalance > 0 ? totalWeightedAPR / totalBalance : 0;
assertApprox(weightedAPR, expectedWeightedAPR, 0.5, `Weighted APR should be approximately ${expectedWeightedAPR.toFixed(2)}%`);
console.log();

// Test Tenor Mix
console.log('Testing Tenor Mix calculation...');
const tenorMix = calculateTenorMix(dataDir);
console.log('   Tenor Mix:', tenorMix);
assert(Object.keys(tenorMix).length === 4, 'Tenor mix should have 4 buckets');
assert(tenorMix['0-12'] !== undefined, 'Should have 0-12 bucket');
assert(tenorMix['13-24'] !== undefined, 'Should have 13-24 bucket');
assert(tenorMix['25-36'] !== undefined, 'Should have 25-36 bucket');
assert(tenorMix['37+'] !== undefined, 'Should have 37+ bucket');
console.log();

// Test Concentration
console.log('Testing Concentration calculation...');
const concentration = calculateConcentration(dataDir);
console.log(`   Top customer: ${concentration.topCustomers[0]?.customerId} - ${concentration.topCustomers[0]?.percentage.toFixed(2)}%`);
assert(concentration.topCustomers.length > 0, 'Should have at least one customer');
assert(concentration.topCustomers[0]!.percentage > 0, 'Top customer percentage should be > 0');
console.log();

// Test NPL
console.log('Testing NPL calculation...');
const npl = calculateNPL(dataDir);
console.log(`   NPL count: ${npl.count}, NPL percentage: ${npl.percentage.toFixed(2)}%`);
// With max DPD of 25 days, no loans should be NPL (>90 days)
assert(npl.count === 0, 'NPL count should be 0 with current test data');
assert(npl.percentage === 0, 'NPL percentage should be 0 with current test data');
console.log();

// Test DPD
console.log('Testing DPD calculation...');
const dpd = calculateDPD(dataDir);
console.log(`   Current: ${dpd.current}, Late: ${dpd.late}, Average DPD: ${dpd.averageDPD.toFixed(2)}`);
assert(dpd.current > 0, 'Should have some current payments');
assert(dpd.late >= 0, 'Late payments should be >= 0');
assert(dpd.averageDPD >= 0, 'Average DPD should be >= 0');
console.log();

// Test Client Goals
console.log('Testing Client Goals calculation...');
const clientGoals = calculateClientGoals(dataDir);
console.log('   Client Goals:', clientGoals);
assert(clientGoals.totalClients > 0, 'Should have total clients > 0');
assert(clientGoals.totalClients === 7, 'Should have 7 unique customers');
assert(clientGoals.recurringClients > 0, 'Should have recurring clients');
assert(clientGoals.recoveredClients > 0, 'Should have recovered clients');
console.log();

// Test All KPIs
console.log('Testing calculateAllKPIs...');
const allKPIs = calculateAllKPIs(dataDir);
assert(allKPIs.outstandingPortfolio > 0, 'All KPIs: Portfolio should be > 0');
assert(allKPIs.weightedAPR > 0, 'All KPIs: Weighted APR should be > 0');
assert(Object.keys(allKPIs.tenorMix).length === 4, 'All KPIs: Tenor mix should have 4 buckets');
assert(allKPIs.concentration.topCustomers.length > 0, 'All KPIs: Should have concentration data');
assert(allKPIs.npl.count >= 0, 'All KPIs: NPL count should be >= 0');
assert(allKPIs.dpd.current >= 0, 'All KPIs: DPD current should be >= 0');
assert(allKPIs.clientGoals.totalClients > 0, 'All KPIs: Should have client goals data');
console.log();

console.log('=== All Tests Passed! ===\n');
