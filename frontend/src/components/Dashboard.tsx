/**
 * Complete Commercial-View KPI Dashboard
 * Enterprise-grade TypeScript React implementation
 */

import React, { useState, useEffect, useCallback } from "react";
import {
  Card,
  Grid,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from "@mui/material";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { TrendingUp, TrendingDown, Warning } from "@mui/icons-material";

interface KPIMetric {
  id: string;
  name: string;
  value: number;
  target: number;
  unit: string;
  description: string;
  trend: "up" | "down" | "stable";
  status: "excellent" | "good" | "warning" | "critical";
}

interface PortfolioData {
  outstandingPortfolio: number;
  activeClients: number;
  weightedAPR: number;
  nplRate: number;
  concentrationRisk: number;
  disbursements: Array<{ month: string; amount: number }>;
  tenorMix: Array<{ tenor: string; percentage: number }>;
  industryBreakdown: Array<{ industry: string; exposure: number }>;
}

interface DashboardProps {
  refreshInterval?: number;
}

const ABACO_COLORS = {
  primary: "#030E19",
  secondary: "#221248",
  neutral: {
    light: "#CED4D9",
    medium: "#9EA9B3",
    dark: "#6D7D8E",
  },
  status: {
    excellent: "#10B981",
    good: "#059669",
    warning: "#F59E0B",
    critical: "#EF4444",
  },
};

export const CommercialViewDashboard: React.FC<DashboardProps> = ({
  refreshInterval = 300000, // 5 minutes
}) => {
  const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(
    null,
  );
  const [kpiMetrics, setKpiMetrics] = useState<KPIMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [portfolioResponse, kpiResponse] = await Promise.all([
        fetch("/api/v1/portfolio-metrics"),
        fetch("/api/v1/kpi-metrics"),
      ]);

      if (!portfolioResponse.ok || !kpiResponse.ok) {
        throw new Error("Failed to fetch dashboard data");
      }

      const portfolioResult = await portfolioResponse.json();
      const kpiResult = await kpiResponse.json();

      setPortfolioData(portfolioResult.data);
      setKpiMetrics(kpiResult.data.metrics);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh data
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Calculate progress percentage
  const calculateProgress = (current: number, target: number): number => {
    return target > 0 ? Math.round((current / target) * 100) : 0;
  };

  // Get status color
  const getStatusColor = (status: string): string => {
    return (
      ABACO_COLORS.status[status as keyof typeof ABACO_COLORS.status] ||
      ABACO_COLORS.neutral.medium
    );
  };

  // Render KPI card
  const renderKPICard = (metric: KPIMetric) => {
    const progress = calculateProgress(metric.value, metric.target);
    const statusColor = getStatusColor(metric.status);

    return (
      <Card
        key={metric.id}
        sx={{
          p: 3,
          height: "100%",
          borderLeft: `4px solid ${statusColor}`,
          "&:hover": { boxShadow: 3 },
        }}
      >
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="flex-start"
        >
          <Box flex={1}>
            <Typography variant="h6" color={ABACO_COLORS.primary} gutterBottom>
              {metric.name}
            </Typography>
            <Typography variant="h4" color={statusColor} fontWeight="bold">
              {metric.value.toLocaleString()}
              {metric.unit}
            </Typography>
            <Typography variant="body2" color={ABACO_COLORS.neutral.dark}>
              Target: {metric.target.toLocaleString()}
              {metric.unit}
            </Typography>
            <Typography
              variant="body2"
              color={ABACO_COLORS.neutral.medium}
              mt={1}
            >
              Progress: {progress}%
            </Typography>
          </Box>
          <Box display="flex" alignItems="center">
            {metric.trend === "up" && <TrendingUp color="success" />}
            {metric.trend === "down" && <TrendingDown color="error" />}
            {metric.status === "critical" && <Warning color="error" />}
          </Box>
        </Box>
        <Typography
          variant="caption"
          color={ABACO_COLORS.neutral.medium}
          mt={2}
        >
          {metric.description}
        </Typography>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="400px"
      >
        <CircularProgress size={60} sx={{ color: ABACO_COLORS.primary }} />
        <Typography variant="h6" ml={2} color={ABACO_COLORS.primary}>
          Loading Commercial-View Dashboard...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        <Typography variant="h6">Dashboard Error</Typography>
        <Typography>{error}</Typography>
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3, bgcolor: "#F8FAFC", minHeight: "100vh" }}>
      {/* Header */}
      <Box mb={4}>
        <Typography
          variant="h3"
          color={ABACO_COLORS.primary}
          fontWeight="bold"
          gutterBottom
        >
          🏦 Commercial-View Dashboard
        </Typography>
        <Typography variant="subtitle1" color={ABACO_COLORS.neutral.dark}>
          Real-time Commercial Lending Analytics • Last updated:{" "}
          {lastUpdated.toLocaleTimeString()}
        </Typography>
      </Box>

      {/* Executive KPI Cards */}
      <Grid container spacing={3} mb={4}>
        {kpiMetrics.map(renderKPICard)}
      </Grid>

      {/* Portfolio Overview Charts */}
      {portfolioData && (
        <Grid container spacing={3} mb={4}>
          {/* Monthly Disbursements */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3, height: 400 }}>
              <Typography
                variant="h6"
                color={ABACO_COLORS.primary}
                gutterBottom
              >
                📈 Monthly Disbursements
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={portfolioData.disbursements}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis
                    tickFormatter={(value) =>
                      `$${(value / 1000000).toFixed(1)}M`
                    }
                  />
                  <Tooltip
                    formatter={(value: number) => [
                      `$${value.toLocaleString()}`,
                      "Amount",
                    ]}
                  />
                  <Line
                    type="monotone"
                    dataKey="amount"
                    stroke={ABACO_COLORS.primary}
                    strokeWidth={3}
                    dot={{ fill: ABACO_COLORS.secondary }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Grid>

          {/* Tenor Mix Distribution */}
          <Grid item xs={12} md={6}>
            <Card sx={{ p: 3, height: 400 }}>
              <Typography
                variant="h6"
                color={ABACO_COLORS.primary}
                gutterBottom
              >
                ⏱️ Tenor Mix Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={portfolioData.tenorMix}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ tenor, percentage }) =>
                      `${tenor}: ${percentage}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="percentage"
                  >
                    {portfolioData.tenorMix.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={Object.values(ABACO_COLORS.status)[index % 4]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </Grid>

          {/* Industry Breakdown */}
          <Grid item xs={12}>
            <Card sx={{ p: 3, height: 400 }}>
              <Typography
                variant="h6"
                color={ABACO_COLORS.primary}
                gutterBottom
              >
                🏭 Industry Exposure Breakdown
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={portfolioData.industryBreakdown}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="industry"
                    angle={-45}
                    textAnchor="end"
                    height={100}
                  />
                  <YAxis
                    tickFormatter={(value) =>
                      `$${(value / 1000000).toFixed(1)}M`
                    }
                  />
                  <Tooltip
                    formatter={(value: number) => [
                      `$${value.toLocaleString()}`,
                      "Exposure",
                    ]}
                  />
                  <Bar dataKey="exposure" fill={ABACO_COLORS.secondary} />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Risk Indicators */}
      <Card sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" color={ABACO_COLORS.primary} gutterBottom>
          🛡️ Risk Management Dashboard
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography
                variant="h4"
                color={ABACO_COLORS.status.excellent}
                fontWeight="bold"
              >
                {portfolioData?.nplRate
                  ? `${(portfolioData.nplRate * 100).toFixed(2)}%`
                  : "N/A"}
              </Typography>
              <Typography variant="body1" color={ABACO_COLORS.neutral.dark}>
                NPL Rate (≥180 days)
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography
                variant="h4"
                color={ABACO_COLORS.status.good}
                fontWeight="bold"
              >
                {portfolioData?.concentrationRisk
                  ? `${(portfolioData.concentrationRisk * 100).toFixed(1)}%`
                  : "N/A"}
              </Typography>
              <Typography variant="body1" color={ABACO_COLORS.neutral.dark}>
                Top Client Concentration
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography
                variant="h4"
                color={ABACO_COLORS.status.warning}
                fontWeight="bold"
              >
                {portfolioData?.weightedAPR
                  ? `${(portfolioData.weightedAPR * 100).toFixed(2)}%`
                  : "N/A"}
              </Typography>
              <Typography variant="body1" color={ABACO_COLORS.neutral.dark}>
                Weighted Average APR
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Card>
    </Box>
  );
};

export default CommercialViewDashboard;
