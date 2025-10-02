/**
 * Configuration Management
 * Handles loading and validation of configuration files
 */

import { DashboardConfig, DataSourceConfig, IntegrationConfig } from '../models/types';

/**
 * Application configuration interface
 */
export interface AppConfig {
  version: string;
  environment: 'development' | 'staging' | 'production';
  dashboards: DashboardConfig[];
  dataSources: DataSourceConfig[];
  integrations: IntegrationConfig[];
  settings: {
    defaultRefreshInterval: number;
    enableAI: boolean;
    enablePredictions: boolean;
    maxHistoricalDataPoints: number;
    logLevel: 'debug' | 'info' | 'warn' | 'error';
  };
}

/**
 * Configuration Manager
 */
export class ConfigManager {
  private config: AppConfig | null = null;

  /**
   * Load configuration from object
   */
  public load(config: AppConfig): void {
    this.validateConfig(config);
    this.config = config;
  }

  /**
   * Get current configuration
   */
  public getConfig(): AppConfig {
    if (!this.config) {
      throw new Error('Configuration not loaded');
    }
    return this.config;
  }

  /**
   * Validate configuration
   */
  private validateConfig(config: AppConfig): void {
    if (!config.version) {
      throw new Error('Configuration version is required');
    }

    if (!['development', 'staging', 'production'].includes(config.environment)) {
      throw new Error('Invalid environment specified');
    }

    if (!Array.isArray(config.dashboards)) {
      throw new Error('Dashboards must be an array');
    }

    if (!Array.isArray(config.dataSources)) {
      throw new Error('Data sources must be an array');
    }

    if (!config.settings || typeof config.settings !== 'object') {
      throw new Error('Settings object is required');
    }
  }

  /**
   * Get default configuration
   */
  public static getDefaultConfig(): AppConfig {
    return {
      version: '1.0.0',
      environment: 'development',
      dashboards: [],
      dataSources: [],
      integrations: [],
      settings: {
        defaultRefreshInterval: 60000, // 1 minute
        enableAI: true,
        enablePredictions: true,
        maxHistoricalDataPoints: 1000,
        logLevel: 'info'
      }
    };
  }

  /**
   * Export configuration to JSON string
   */
  public exportConfig(): string {
    if (!this.config) {
      throw new Error('Configuration not loaded');
    }
    return JSON.stringify(this.config, null, 2);
  }

  /**
   * Update settings
   */
  public updateSettings(settings: Partial<AppConfig['settings']>): void {
    if (!this.config) {
      throw new Error('Configuration not loaded');
    }
    this.config.settings = { ...this.config.settings, ...settings };
  }
}
