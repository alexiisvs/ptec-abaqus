import * as echarts from "echarts";
import { useEffect, useRef } from "react";

export default function PortfolioWeightsChart({ data }) {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!chartRef.current || !data) {
      return undefined;
    }

    const chart = echarts.init(chartRef.current);
    const dates = data.series?.map((item) => item.date) || [];
    const assets = data.assets || [];

    chart.setOption({
      tooltip: {
        trigger: "axis",
        valueFormatter: (value) => `${Number(value).toFixed(2)}%`,
      },
      legend: {
        type: "scroll",
        top: 0,
      },
      grid: {
        top: 72,
        right: 24,
        bottom: 36,
        left: 56,
      },
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: dates,
      },
      yAxis: {
        type: "value",
        max: 100,
        axisLabel: {
          formatter: "{value}%",
        },
      },
      series: assets.map((asset) => ({
        name: asset.name,
        type: "line",
        stack: "weights",
        areaStyle: {},
        emphasis: {
          focus: "series",
        },
        showSymbol: false,
        data: data.series.map((item) => Number(item.weights[asset.name] || 0) * 100),
      })),
    });

    const resizeObserver = new ResizeObserver(() => chart.resize());
    resizeObserver.observe(chartRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.dispose();
    };
  }, [data]);

  return <div className="chart-canvas" ref={chartRef} />;
}
