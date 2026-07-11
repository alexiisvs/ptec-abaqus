import * as echarts from "echarts";
import { useEffect, useRef, useState } from "react";

export default function PortfolioWeightsChart({ data }) {
  const chartRef = useRef(null);
  const [selectedAssetName, setSelectedAssetName] = useState("");
  const [hoveredAssetName, setHoveredAssetName] = useState("");

  useEffect(() => {
    if (!chartRef.current || !data) {
      return undefined;
    }

    const chart = echarts.init(chartRef.current);
    const dates = data.series?.map((item) => item.date) || [];
    const assets = (data.assets || []).filter((asset) =>
      data.series?.some((item) => Number(item.weights[asset.name] || 0) > 0),
    );
    const highlightedAssetName = hoveredAssetName || selectedAssetName;

    chart.setOption({
      tooltip: {
        trigger: "axis",
        formatter: (params) => {
          const date = params[0]?.axisValue || "";
          const rows = params
            .map((param) => {
              const isSelected = param.seriesName === highlightedAssetName;
              const weight = `${Number(param.value).toFixed(2)}%`;
              const style = isSelected ? "font-weight: 800;" : "";

              return `
                <div style="${style}">
                  ${param.marker}${param.seriesName}
                  <span style="float:right;margin-left:20px;">${weight}</span>
                </div>
              `;
            })
            .join("");

          return `<strong>${date}</strong>${rows}`;
        },
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
      series: assets.map((asset) => {
        const isSelected = asset.name === highlightedAssetName;
        const hasSelection = highlightedAssetName !== "";

        return {
          name: asset.name,
          type: "line",
          stack: "weights",
          areaStyle: {
            opacity: hasSelection ? (isSelected ? 0.82 : 0.08) : 0.42,
          },
          emphasis: {
            focus: "series",
            lineStyle: {
              width: 4,
            },
          },
          lineStyle: {
            opacity: hasSelection ? (isSelected ? 1 : 0.18) : 1,
            width: isSelected ? 3 : 1.5,
          },
          showSymbol: false,
          data: data.series.map((item) => Number(item.weights[asset.name] || 0) * 100),
        };
      }),
    });

    chart.on("click", (params) => {
      if (!params.seriesName) {
        return;
      }

      setSelectedAssetName((currentAssetName) =>
        currentAssetName === params.seriesName ? "" : params.seriesName,
      );
    });

    chart.on("mouseover", (params) => {
      if (params.seriesName) {
        setHoveredAssetName(params.seriesName);
      }
    });

    chart.on("globalout", () => {
      setHoveredAssetName("");
    });

    const resizeObserver = new ResizeObserver(() => chart.resize());
    resizeObserver.observe(chartRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.dispose();
    };
  }, [data, selectedAssetName, hoveredAssetName]);

  return <div className="chart-canvas" ref={chartRef} />;
}
