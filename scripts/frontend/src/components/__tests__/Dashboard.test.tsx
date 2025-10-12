/**
 * Comprehensive Dashboard Component Test Suite
 * Tests React TypeScript dashboard with all KPI components
 */

import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { jest } from "@jest/globals";
import "@testing-library/jest-dom";
import { CommercialViewDashboard } from "../Dashboard";

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock chart components to avoid canvas issues in tests
jest.mock("recharts", () => ({
  LineChart: ({ children }: any) => (
    <div data-testid="line-chart">{children}</div>
  ),
  Line: () => <div data-testid="line" />,
  BarChart: ({ children }: any) => (
    <div data-testid="bar-chart">{children}</div>
  ),
  Bar: () => <div data-testid="bar" />,
  PieChart: ({ children }: any) => (
    <div data-testid="pie-chart">{children}</div>
  ),
  Pie: () => <div data-testid="pie" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  Cell: () => <div data-testid="cell" />,
}));

describe("CommercialViewDashboard", () => {
  const mockPortfolioData = {
    outstandingPortfolio: 7800000,
    activeClients: 150,
    weightedAPR: 0.185,
    nplRate: 0.025,
    concentrationRisk: 0.12,
    disbursements: [
      { month: "Jan", amount: 450000 },
      { month: "Feb", amount: 520000 },
      { month: "Mar", amount: 480000 },
    ],
    tenorMix: [
      { tenor: "0-12 months", percentage: 25 },
      { tenor: "13-24 months", percentage: 35 },
      { tenor: "25-36 months", percentage: 25 },
      { tenor: "37+ months", percentage: 15 },
    ],
    industryBreakdown: [
      { industry: "Construction", exposure: 2500000 },
      { industry: "Real Estate", exposure: 2000000 },
      { industry: "Manufacturing", exposure: 1800000 },
    ],
  };

  const mockKPIMetrics = [
    {
      id: "outstanding_portfolio",
      name: "Outstanding Portfolio",
      value: 7800000,
      target: 7800000,
      unit: "$",
      description: "Total outstanding loan balances",
      trend: "up",
      status: "excellent",
    },
    {
      id: "weighted_apr",
      name: "Weighted APR",
      value: 18.5,
      target: 18.5,
      unit: "%",
      description: "Portfolio weighted average interest rate",
      trend: "stable",
      status: "good",
    },
  ];

  beforeEach(() => {
    mockFetch.mockClear();
  });

  // Test Case 1: Loading State
  test("displays loading state initially", () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<CommercialViewDashboard />);

    expect(
      screen.getByText("Loading Commercial-View Dashboard..."),
    ).toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  // Test Case 2: Successful Data Loading
  test("loads and displays dashboard data successfully", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPortfolioData }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: { metrics: mockKPIMetrics } }),
      });

    render(<CommercialViewDashboard />);

    await waitFor(() => {
      expect(
        screen.getByText("🏦 Commercial-View Dashboard"),
      ).toBeInTheDocument();
    });

    // Check KPI cards are rendered
    expect(screen.getByText("Outstanding Portfolio")).toBeInTheDocument();
    expect(screen.getByText("Weighted APR")).toBeInTheDocument();
    expect(screen.getByText("$7,800,000")).toBeInTheDocument();
    expect(screen.getByText("18.5%")).toBeInTheDocument();
  });

  // Test Case 3: Error Handling
  test("displays error message when data loading fails", async () => {
    mockFetch.mockRejectedValue(new Error("Network error"));

    render(<CommercialViewDashboard />);

    await waitFor(() => {
      expect(screen.getByText("Dashboard Error")).toBeInTheDocument();
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });
  });

  // Test Case 4: KPI Card Rendering
  test("renders KPI cards with correct formatting", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPortfolioData }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: { metrics: mockKPIMetrics } }),
      });

    render(<CommercialViewDashboard />);

    await waitFor(() => {
      // Check progress calculation
      expect(screen.getByText("Progress: 100%")).toBeInTheDocument();

      // Check target display
      expect(screen.getByText("Target: 7,800,000$")).toBeInTheDocument();
      expect(screen.getByText("Target: 18.5%")).toBeInTheDocument();
    });
  });

  // Test Case 5: Chart Components
  test("renders all chart components", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPortfolioData }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: { metrics: mockKPIMetrics } }),
      });

    render(<CommercialViewDashboard />);

    await waitFor(() => {
      expect(screen.getByTestId("line-chart")).toBeInTheDocument();
      expect(screen.getByTestId("pie-chart")).toBeInTheDocument();
      expect(screen.getByTestId("bar-chart")).toBeInTheDocument();
    });
  });

  // Test Case 6: Status Color Coding
  test("applies correct status colors to KPI cards", async () => {
    const criticalKPI = {
      ...mockKPIMetrics[0],
      status: "critical",
      value: 5000000, // Well below target
    };

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPortfolioData }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: { metrics: [criticalKPI] } }),
      });

    render(<CommercialViewDashboard />);

    await waitFor(() => {
      const card = screen
        .getByText("Outstanding Portfolio")
        .closest(".MuiCard-root");
      expect(card).toHaveStyle("border-left: 4px solid #EF4444"); // Critical red
    });
  });

  // Test Case 7: Auto-refresh Functionality
  test("auto-refreshes data at specified interval", async () => {
    const refreshInterval = 1000; // 1 second for testing

    mockFetch
      .mockResolvedValue({
        ok: true,
        json: async () => ({ data: mockPortfolioData }),
      })
      .mockResolvedValue({
        ok: true,
        json: async () => ({ data: { metrics: mockKPIMetrics } }),
      });

    render(<CommercialViewDashboard refreshInterval={refreshInterval} />);

    // Initial load
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    // Wait for refresh
    await waitFor(
      () => {
        expect(mockFetch).toHaveBeenCalledTimes(4);
      },
      { timeout: 1500 },
    );
  });

  // Test Case 8: Responsive Design
  test("renders responsively on different screen sizes", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPortfolioData }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: { metrics: mockKPIMetrics } }),
      });

    // Mock different screen sizes
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 768, // Tablet size
    });

    render(<CommercialViewDashboard />);

    await waitFor(() => {
      // Grid should adapt to smaller screens
      const gridItems = screen.getAllByRole("grid");
      expect(gridItems.length).toBeGreaterThan(0);
    });
  });

  // Test Case 9: Accessibility
  test("meets accessibility standards", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPortfolioData }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: { metrics: mockKPIMetrics } }),
      });

    render(<CommercialViewDashboard />);

    await waitFor(() => {
      // Check for proper heading structure
      expect(screen.getByRole("heading", { level: 3 })).toBeInTheDocument();

      // Check for proper ARIA labels
      expect(screen.getByRole("progressbar")).toHaveAttribute("aria-label");
    });
  });

  // Test Case 10: Data Formatting
  test("formats currency and percentage values correctly", async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPortfolioData }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: { metrics: mockKPIMetrics } }),
      });

    render(<CommercialViewDashboard />);

    await waitFor(() => {
      // Check currency formatting
      expect(screen.getByText("$7,800,000")).toBeInTheDocument();

      // Check percentage formatting
      expect(screen.getByText("18.5%")).toBeInTheDocument();
      expect(screen.getByText("2.50%")).toBeInTheDocument(); // NPL rate
    });
  });
});
