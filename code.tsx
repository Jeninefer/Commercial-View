// code.tsx — Figma Widget (React)
// Brand: Lato/Poppins; Colors: #030E19, #221248, #6D7D8E, #9EA9B3, #CED4D9, #FFFFFF

const { widget } = figma;
const { AutoLayout, Text, Input, Line, Frame, Rectangle, SVG } = widget;

type SeriesPoint = { month: string; amount?: number; ["Active Clients"]?: number; };
type KPI = {
  outstanding_portfolio: number;
  active_clients: number;
  weighted_apr: number | null;
  npl_180_amount: number;
  top10_concentration_pct: number | null;
};

type TargetComparison = {
  current: number;
  target: number;
  percentage?: number | null;
  within_tolerance: boolean;
};

type Payload = {
  as_of: string;
  executive_kpis: KPI;
  target_comparisons?: {
    outstanding?: TargetComparison;
    apr?: TargetComparison;
    npl?: TargetComparison;
  };
  monthly_series: {
    disbursements: { month: string; amount: number }[];
    active_clients: { month: string; ["Active Clients"]: number }[];
  };
  tenor_mix_pct: Record<string, number>;
  tenor_target_comparisons?: Record<string, {
    current: number;
    target: number;
    within_tolerance: boolean;
  }>;
  kam_breakdown: { KAM: string; outstanding: number }[];
  sector_breakdown: { sector: string; outstanding: number }[];
  revenue: { by_month: any[] };
  capital_plan_q4: { month: string; planned_disbursement: number }[];
  mappings: any;
};

function fmtMoney(n?: number) {
  if (n == null) return "-";
  return "$" + Math.round(n).toLocaleString();
}

function fmtPct(n?: number | null) {
  if (n == null) return "-";
  return (Math.round(n * 10) / 10).toFixed(1) + "%";
}

function monthLabel(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString("en-US", { month: "short", year: "2-digit" });
}

function Chart({ 
  data, 
  color = "#221248", 
  w = 720, 
  h = 220 
}: { 
  data: { x: string; y: number }[]; 
  color?: string; 
  w?: number; 
  h?: number;
}) {
  if (!data || data.length === 0) {
    return <Text fill="#6D7D8E">No data</Text>;
  }
  
  const pad = 24;
  const xs = data.map(d => d.x);
  const ys = data.map(d => d.y);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const rng = Math.max(1, maxY - minY);
  const sx = (i: number) => pad + (i * (w - 2 * pad)) / Math.max(1, data.length - 1);
  const sy = (v: number) => h - pad - ((v - minY) * (h - 2 * pad)) / rng;

  const series = data.map((d, i) => ({ x: sx(i), y: sy(d.y) }));
  const pathData = series.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");

  return (
    <AutoLayout direction="vertical" spacing={8}>
      <Frame width={w} height={h} fill="#FFFFFF" cornerRadius={12} stroke="#CED4D9">
        <SVG 
          src={`<svg width="${w}" height="${h}"><path d="${pathData}" stroke="${color}" stroke-width="2" fill="none" /></svg>`}
        />
      </Frame>
      <AutoLayout spacing={12}>
        {xs.map((m, i) => (
          <Text key={i} fontSize={10} fill="#6D7D8E">{m}</Text>
        ))}
      </AutoLayout>
    </AutoLayout>
  );
}

function Tile({ 
  title, 
  value, 
  subtitle,
  target,
  status
}: { 
  title: string; 
  value: string; 
  subtitle?: string;
  target?: string;
  status?: "good" | "warning" | "bad";
}) {
  const statusColors = {
    good: "#10B981",
    warning: "#F59E0B",
    bad: "#EF4444"
  };
  
  return (
    <AutoLayout 
      direction="vertical" 
      padding={16} 
      fill="#FFFFFF" 
      cornerRadius={12} 
      stroke={status ? statusColors[status] : "#CED4D9"}
      strokeWidth={status ? 2 : 1}
      spacing={6} 
      width={220}
    >
      <Text fontFamily="Lato" fontSize={12} fill="#6D7D8E">{title}</Text>
      <Text fontFamily="Poppins" fontSize={20} fill="#030E19">{value}</Text>
      {target && (
        <Text fontSize={11} fill="#221248">Target: {target}</Text>
      )}
      {subtitle && <Text fontSize={10} fill="#9EA9B3">{subtitle}</Text>}
    </AutoLayout>
  );
}

function TargetIndicator({ 
  comparison 
}: { 
  comparison?: TargetComparison;
}) {
  if (!comparison) return null;
  
  const status = comparison.within_tolerance ? "good" : "warning";
  const statusIcon = comparison.within_tolerance ? "✓" : "⚠";
  
  return (
    <AutoLayout spacing={4} padding={4} cornerRadius={4} fill={status === "good" ? "#DCFCE7" : "#FEF3C7"}>
      <Text fontSize={10} fill={status === "good" ? "#166534" : "#92400E"}>
        {statusIcon} {comparison.percentage ? `${comparison.percentage.toFixed(1)}%` : ""}
      </Text>
    </AutoLayout>
  );
}

export default function () {
  const [raw, setRaw] = widget.useSyncedState("raw", "");
  const [data, setData] = widget.useSyncedState<Payload | null>("data", null);

  const applyJSON = () => {
    try {
      const obj = JSON.parse(raw) as Payload;
      setData(obj);
      figma.notify("Dashboard updated successfully!");
    } catch (e) {
      figma.notify("Invalid JSON - please check formatting");
    }
  };

  const header = (
    <AutoLayout 
      direction="vertical" 
      padding={16} 
      fill="#030E19" 
      cornerRadius={12} 
      spacing={4} 
      width={960}
    >
      <Text fontFamily="Poppins" fontSize={20} fill="#FFFFFF">
        Executive KPIs Snapshot
      </Text>
      <Text fontSize={12} fill="#CED4D9">
        As of {data?.as_of || "-"}
      </Text>
    </AutoLayout>
  );

  const k = data?.executive_kpis;
  const tc = data?.target_comparisons;
  
  // Determine status for outstanding portfolio
  const outstandingStatus = tc?.outstanding?.within_tolerance ? "good" : 
                            tc?.outstanding ? "warning" : undefined;
  
  const aprStatus = tc?.apr?.within_tolerance ? "good" : 
                   tc?.apr ? "warning" : undefined;
  
  const nplStatus = tc?.npl?.within_tolerance ? "good" : 
                   tc?.npl ? "warning" : undefined;
  
  const tiles = (
    <AutoLayout spacing={12} wrap>
      <Tile 
        title="Outstanding Portfolio" 
        value={fmtMoney(k?.outstanding_portfolio)} 
        target={tc?.outstanding ? fmtMoney(tc.outstanding.target) : undefined}
        subtitle={tc?.outstanding ? `${tc.outstanding.percentage?.toFixed(1)}% of target` : "Source: Payment Schedule"}
        status={outstandingStatus}
      />
      <Tile 
        title="Active Clients" 
        value={(k?.active_clients ?? "-").toString()} 
        subtitle="Source: Loan Data"
      />
      <Tile 
        title="Weighted APR" 
        value={fmtPct(k?.weighted_apr)}
        target={tc?.apr ? fmtPct(tc.apr.target) : undefined}
        subtitle={tc?.apr ? `Target: ${tc.apr.target.toFixed(1)}%` : "Σ(APR×Outstanding)/Σ(Outstanding)"}
        status={aprStatus}
      />
      <Tile 
        title="NPL ≥180" 
        value={fmtMoney(k?.npl_180_amount)}
        target={tc?.npl ? `${tc.npl.target.toFixed(1)}%` : undefined}
        subtitle={tc?.npl ? `${tc.npl.current.toFixed(1)}% of portfolio` : "Source: PS × Historic"}
        status={nplStatus}
      />
      <Tile 
        title="Top-10 Concentration" 
        value={fmtPct(k?.top10_concentration_pct)} 
        subtitle="Top10 / Total Outstanding"
      />
    </AutoLayout>
  );

  // "Línea gráfica" → monthly disbursements
  const disb = (data?.monthly_series?.disbursements || []).map(d => ({ 
    x: monthLabel(d.month), 
    y: d.amount || 0 
  }));
  
  const chart = (
    <AutoLayout direction="vertical" spacing={8}>
      <Text fontFamily="Poppins" fontSize={16} fill="#221248">
        Monthly Disbursements (Line Chart)
      </Text>
      <Chart data={disb} color="#221248" />
    </AutoLayout>
  );

  // KAM breakdown (top 8)
  const kamRows = (data?.kam_breakdown || []).slice(0, 8).map((r, i) => (
    <AutoLayout 
      key={i} 
      width={460} 
      spacing={8} 
      padding={{vertical:6, horizontal:8}} 
      fill="#FFFFFF" 
      cornerRadius={8} 
      stroke="#ECEFF2" 
      horizontalAlignItems="space-between"
    >
      <Text fontSize={12} fill="#030E19">{r.KAM || "—"}</Text>
      <Text fontSize={12} fill="#221248">{fmtMoney(r.outstanding)}</Text>
    </AutoLayout>
  ));

  // Tenor mix with target comparisons
  const tm = data?.tenor_mix_pct || {};
  const ttc = data?.tenor_target_comparisons || {};
  
  const tmRows = Object.entries(tm).map(([k, v], i) => {
    const target = ttc[k];
    const status = target?.within_tolerance ? "✓" : target ? "⚠" : "";
    
    return (
      <AutoLayout 
        key={i} 
        spacing={8} 
        padding={{vertical:6, horizontal:8}} 
        fill="#FFFFFF" 
        cornerRadius={8} 
        stroke={target?.within_tolerance ? "#10B981" : target ? "#F59E0B" : "#ECEFF2"}
        horizontalAlignItems="space-between" 
        width={220}
      >
        <Text fontSize={12} fill="#030E19">{k}</Text>
        <AutoLayout spacing={4}>
          <Text fontSize={12} fill="#221248">{v.toFixed(1)}%</Text>
          {target && (
            <Text fontSize={10} fill="#6D7D8E">
              ({status} {target.target.toFixed(1)}%)
            </Text>
          )}
        </AutoLayout>
      </AutoLayout>
    );
  });

  return (
    <AutoLayout direction="vertical" spacing={16} padding={16} fill="#F7F8FA">
      <AutoLayout 
        direction="vertical" 
        spacing={8} 
        padding={12} 
        fill="#FFFFFF" 
        cornerRadius={12} 
        stroke="#CED4D9" 
        width={960}
      >
        <Text fontFamily="Poppins" fontSize={16} fill="#030E19">
          Paste JSON from dashboard_payload.json
        </Text>
        <Input 
          value={raw} 
          placeholder='Paste JSON here' 
          onTextEditEnd={(e) => setRaw(e.characters)} 
          width={920} 
          height={140} 
          inputBehavior="multiline"
        />
        <AutoLayout 
          padding={10}
          cornerRadius={8} 
          fill="#221248" 
          onClick={applyJSON}
        >
          <Text fill="#FFFFFF" fontFamily="Poppins" fontSize={14}>Apply JSON</Text>
        </AutoLayout>
      </AutoLayout>

      {header}

      {data ? (
        <>
          {tiles}
          
          <AutoLayout spacing={16}>
            {chart}
            
            <AutoLayout direction="vertical" spacing={8}>
              <Text fontFamily="Poppins" fontSize={16} fill="#221248">
                KAM Breakdown (Outstanding)
              </Text>
              {kamRows.length ? kamRows : <Text fill="#6D7D8E">No KAM data.</Text>}
              
              <Text fontFamily="Poppins" fontSize={16} fill="#221248" padding={{top:12}}>
                Tenor Mix
              </Text>
              <AutoLayout spacing={8} wrap>
                {tmRows}
              </AutoLayout>
            </AutoLayout>
          </AutoLayout>

          <Text fontSize={10} fill="#9EA9B3" padding={{top:8}}>
            Sources: Payment Schedule (Outstanding, NPL), Loan Data (APR, Tenor, Clients), 
            Historic Real Payment (Collections). KAM & LineaCredito: Google Sheets "{data.mappings.data_sheet}" 
            and range "{data.mappings.desembolsos_range}". Targets loaded from Q4_Targets.csv.
          </Text>
          
          {(tc?.outstanding || tc?.apr || tc?.npl) && (
            <AutoLayout 
              direction="vertical" 
              spacing={6} 
              padding={12} 
              fill="#FEF3C7" 
              cornerRadius={8}
              width={960}
            >
              <Text fontFamily="Poppins" fontSize={14} fill="#92400E">
                Target Status Summary
              </Text>
              {tc?.outstanding && (
                <Text fontSize={11} fill="#78350F">
                  Outstanding: {tc.outstanding.percentage?.toFixed(1)}% of target 
                  ({tc.outstanding.within_tolerance ? "✓ Within tolerance" : "⚠ Outside tolerance"})
                </Text>
              )}
              {tc?.apr && (
                <Text fontSize={11} fill="#78350F">
                  APR: {tc.apr.current.toFixed(2)}% vs {tc.apr.target.toFixed(2)}% target 
                  ({tc.apr.within_tolerance ? "✓ Within tolerance" : "⚠ Outside tolerance"})
                </Text>
              )}
              {tc?.npl && (
                <Text fontSize={11} fill="#78350F">
                  NPL: {tc.npl.current.toFixed(2)}% vs {tc.npl.target.toFixed(2)}% target 
                  ({tc.npl.within_tolerance ? "✓ Within tolerance" : "⚠ Outside tolerance"})
                </Text>
              )}
            </AutoLayout>
          )}
        </>
      ) : (
        <Text fill="#6D7D8E">Waiting for JSON…</Text>
      )}
    </AutoLayout>
  );
}
