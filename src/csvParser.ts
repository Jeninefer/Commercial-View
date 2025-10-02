import * as fs from 'fs';
import * as path from 'path';

export interface CSVRow {
  [key: string]: string;
}

/**
 * Parse a CSV file and return array of objects
 */
export function parseCSV(filePath: string): CSVRow[] {
  const absolutePath = path.resolve(filePath);
  const content = fs.readFileSync(absolutePath, 'utf-8');
  const lines = content.trim().split('\n');
  
  if (lines.length === 0) {
    return [];
  }
  
  const headers = lines[0]?.split(',').map(h => h.trim()) || [];
  const rows: CSVRow[] = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i]?.split(',').map(v => v.trim()) || [];
    const row: CSVRow = {};
    
    headers.forEach((header, index) => {
      row[header] = values[index] || '';
    });
    
    rows.push(row);
  }
  
  return rows;
}

/**
 * Convert string to number, handling empty strings
 */
export function toNumber(value: string): number {
  const num = parseFloat(value);
  return isNaN(num) ? 0 : num;
}

/**
 * Convert date string to Date object
 */
export function toDate(value: string): Date {
  return new Date(value);
}
