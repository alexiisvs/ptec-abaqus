import * as echarts from "echarts";
import { useEffect, useRef } from "react";

function formatUsd(value) {
  return `$${Number(value).toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
}

export default function PortfolioValueChart({ data, visiblePortfolioIds }) {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!chartRef.current || !data) {
      return undefined;
    }

    const chart = echarts.init(chartRef.current);
    const dates = data.portfolios?.[0]?.series.map((item) => item.date) || [];
    const portfolios =
      data.portfolios?.filter((portfolio) => visiblePortfolioIds.includes(String(portfolio.id))) || [];

    chart.setOption({
      color: ["#1f7a8c", "#bf6f30"],
      tooltip: {
        trigger: "axis",
        valueFormatter: formatUsd,
      },
      legend: {
        top: 0,
      },
      grid: {
        top: 48,
        right: 24,
        bottom: 36,
        left: 78,
      },
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: dates,
      },
      yAxis: {
        type: "value",
        axisLabel: {
          formatter: (value) => `$${Math.round(value / 1000000)}M`,
        },
      },
      series:
        portfolios.map((portfolio) => ({
          name: portfolio.name,
          type: "line",
          smooth: true,
          showSymbol: false,
          data: portfolio.series.map((item) => Number(item.value)),
        })) || [],
    });

    const resizeObserver = new ResizeObserver(() => chart.resize());
    resizeObserver.observe(chartRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.dispose();
    };
  }, [data, visiblePortfolioIds]);

  return <div className="chart-canvas" ref={chartRef} />;
}
