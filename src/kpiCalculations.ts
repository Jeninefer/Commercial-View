import { parseCSV, toNumber, CSVRow } from './csvParser';
import * as path from 'path';

export interface KPIData {
  outstandingPortfolio: number;
  weightedAPR: number;
  tenorMix: {
    [bucket: string]: number;
  };
  concentration: {
    topCustomers: Array<{ customerId: string; balance: number; percentage: number }>;
  };
  npl: {
    count: number;
    percentage: number;
  };
  dpd: {
    current: number;
    late: number;
    averageDPD: number;
  };
  clientGoals: {
    totalClients: number;
    newClients: number;
    recurringClients: number;
    recoveredClients: number;
  };
}

export interface Q4Targets {
  outstandingPortfolio: number;
  weightedAPR: number;
  tenorMix: {
    [bucket: string]: number;
  };
  concentration: number;
  npl: number;
  dpd: number;
  clientGoals: {
    totalClients: number;
    newClients: number;
    recurringClients: number;
    recoveredClients: number;
  };
}

/**
 * Calculate progress percentage
 */
export function calcProgress(current: number, target: number): number {
  if (target === 0) return 0;
  return Math.round((current / target) * 100);
}

/**
 * Calculate outstanding portfolio from Payment Schedule
 * Sum of most recent EOM balances
 */
export function calculateOutstandingPortfolio(dataDir: string): number {
  const paymentSchedule = parseCSV(path.join(dataDir, 'payment_schedule.csv'));
  
  // Group by LoanID and get the latest balance
  const latestBalances = new Map<string, number>();
  
  paymentSchedule.forEach(row => {
    const loanId = row.LoanID || '';
    const balance = toNumber(row.EOMBalance || '0');
    const paymentDate = new Date(row.PaymentDate || '');
    
    const existing = latestBalances.get(loanId);
    if (!existing || existing < balance) {
      latestBalances.set(loanId, balance);
    }
  });
  
  // Sum all latest balances
  let total = 0;
  latestBalances.forEach(balance => {
    total += balance;
  });
  
  return total;
}

/**
 * Calculate weighted APR from Loan Data
 * Weighted average: sum(APR × balance) / sum(balance)
 */
export function calculateWeightedAPR(dataDir: string): number {
  const loanData = parseCSV(path.join(dataDir, 'loan_data.csv'));
  
  let totalWeighted = 0;
  let totalBalance = 0;
  
  loanData.forEach(row => {
    if (row.Status === 'Active') {
      const apr = toNumber(row.APR || '0');
      const balance = toNumber(row.CurrentBalance || '0');
      
      totalWeighted += apr * balance;
      totalBalance += balance;
    }
  });
  
  if (totalBalance === 0) return 0;
  return totalWeighted / totalBalance;
}

/**
 * Calculate tenor mix from Loan Data
 * Group by tenor buckets: 0-12, 13-24, 25-36, 37+
 */
export function calculateTenorMix(dataDir: string): { [bucket: string]: number } {
  const loanData = parseCSV(path.join(dataDir, 'loan_data.csv'));
  
  const buckets = {
    '0-12': 0,
    '13-24': 0,
    '25-36': 0,
    '37+': 0
  };
  
  loanData.forEach(row => {
    if (row.Status === 'Active') {
      const tenor = toNumber(row.TenorMonths || '0');
      const balance = toNumber(row.CurrentBalance || '0');
      
      if (tenor <= 12) {
        buckets['0-12'] += balance;
      } else if (tenor <= 24) {
        buckets['13-24'] += balance;
      } else if (tenor <= 36) {
        buckets['25-36'] += balance;
      } else {
        buckets['37+'] += balance;
      }
    }
  });
  
  return buckets;
}

/**
 * Calculate concentration from Payment Schedule
 * Top customers by outstanding balance
 */
export function calculateConcentration(dataDir: string): {
  topCustomers: Array<{ customerId: string; balance: number; percentage: number }>;
} {
  const paymentSchedule = parseCSV(path.join(dataDir, 'payment_schedule.csv'));
  
  // Group by CustomerID and get latest balance per loan
  const customerBalances = new Map<string, Map<string, number>>();
  
  paymentSchedule.forEach(row => {
    const customerId = row.CustomerID || '';
    const loanId = row.LoanID || '';
    const balance = toNumber(row.EOMBalance || '0');
    
    if (!customerBalances.has(customerId)) {
      customerBalances.set(customerId, new Map());
    }
    
    const loans = customerBalances.get(customerId)!;
    const existingBalance = loans.get(loanId) || 0;
    if (balance > existingBalance) {
      loans.set(loanId, balance);
    }
  });
  
  // Sum balances per customer
  const customerTotals = new Map<string, number>();
  let totalPortfolio = 0;
  
  customerBalances.forEach((loans, customerId) => {
    let customerTotal = 0;
    loans.forEach(balance => {
      customerTotal += balance;
    });
    customerTotals.set(customerId, customerTotal);
    totalPortfolio += customerTotal;
  });
  
  // Sort and get top customers
  const sortedCustomers = Array.from(customerTotals.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10); // Top 10 customers
  
  const topCustomers = sortedCustomers.map(([customerId, balance]) => ({
    customerId,
    balance,
    percentage: totalPortfolio > 0 ? (balance / totalPortfolio) * 100 : 0
  }));
  
  return { topCustomers };
}

/**
 * Calculate NPL (Non-Performing Loans) from Historic Real Payment
 * Loans with DPD > 90 days
 */
export function calculateNPL(dataDir: string): { count: number; percentage: number } {
  const historicPayments = parseCSV(path.join(dataDir, 'historic_real_payment.csv'));
  
  // Get unique loans and their max DPD
  const loanMaxDPD = new Map<string, number>();
  
  historicPayments.forEach(row => {
    const loanId = row.LoanID || '';
    const dpd = toNumber(row.DaysPastDue || '0');
    
    const existingDPD = loanMaxDPD.get(loanId) || 0;
    if (dpd > existingDPD) {
      loanMaxDPD.set(loanId, dpd);
    }
  });
  
  const totalLoans = loanMaxDPD.size;
  let nplCount = 0;
  
  loanMaxDPD.forEach(dpd => {
    if (dpd > 90) {
      nplCount++;
    }
  });
  
  return {
    count: nplCount,
    percentage: totalLoans > 0 ? (nplCount / totalLoans) * 100 : 0
  };
}

/**
 * Calculate DPD (Days Past Due) metrics from Historic Real Payment
 */
export function calculateDPD(dataDir: string): {
  current: number;
  late: number;
  averageDPD: number;
} {
  const historicPayments = parseCSV(path.join(dataDir, 'historic_real_payment.csv'));
  
  let currentCount = 0;
  let lateCount = 0;
  let totalDPD = 0;
  let totalPayments = historicPayments.length;
  
  historicPayments.forEach(row => {
    const dpd = toNumber(row.DaysPastDue || '0');
    
    if (dpd === 0) {
      currentCount++;
    } else {
      lateCount++;
    }
    
    totalDPD += dpd;
  });
  
  return {
    current: currentCount,
    late: lateCount,
    averageDPD: totalPayments > 0 ? totalDPD / totalPayments : 0
  };
}

/**
 * Calculate client goals from Loan Data
 */
export function calculateClientGoals(dataDir: string): {
  totalClients: number;
  newClients: number;
  recurringClients: number;
  recoveredClients: number;
} {
  const loanData = parseCSV(path.join(dataDir, 'loan_data.csv'));
  
  const uniqueCustomers = new Set<string>();
  let newClients = 0;
  let recurringClients = 0;
  let recoveredClients = 0;
  
  // Track customers
  const customerInfo = new Map<string, { isRecurring: boolean; isRecovered: boolean; firstSeen: Date }>();
  
  loanData.forEach(row => {
    const customerId = row.CustomerID || '';
    const isRecurring = row.RecurringCustomer === 'Yes';
    const status = row.Status || '';
    const firstSeen = new Date(row.FirstSeen || '');
    
    uniqueCustomers.add(customerId);
    
    if (!customerInfo.has(customerId)) {
      customerInfo.set(customerId, {
        isRecurring,
        isRecovered: status === 'Recovered',
        firstSeen
      });
    } else {
      // Update info if recovered
      const info = customerInfo.get(customerId);
      if (!info) {
        return;
      }
      if (status === 'Recovered') {
        info.isRecovered = true;
      }
      if (isRecurring) {
        info.isRecurring = true;
      }
    }
  });
  
  // Count by category
  const currentYear = new Date().getFullYear();
  
  customerInfo.forEach(info => {
    if (info.isRecurring) {
      recurringClients++;
    } else if (info.firstSeen.getFullYear() === currentYear) {
      newClients++;
    }
    
    if (info.isRecovered) {
      recoveredClients++;
    }
  });
  
  return {
    totalClients: uniqueCustomers.size,
    newClients,
    recurringClients,
    recoveredClients
  };
}

/**
 * Calculate all KPIs from CSV data
 */
export function calculateAllKPIs(dataDir: string): KPIData {
  return {
    outstandingPortfolio: calculateOutstandingPortfolio(dataDir),
    weightedAPR: calculateWeightedAPR(dataDir),
    tenorMix: calculateTenorMix(dataDir),
    concentration: calculateConcentration(dataDir),
    npl: calculateNPL(dataDir),
    dpd: calculateDPD(dataDir),
    clientGoals: calculateClientGoals(dataDir)
  };
}
