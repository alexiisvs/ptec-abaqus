import { useEffect, useState } from "react";

import { fetchPortfolioValue, fetchPortfolioWeights } from "./api";
import PortfolioValueChart from "./components/PortfolioValueChart";
import PortfolioWeightsChart from "./components/PortfolioWeightsChart";

const DEFAULT_START_DATE = "2022-02-15";
const DEFAULT_END_DATE = "2023-02-16";

const QUICK_RANGES = {
  manual: null,
  "5d": { days: 5 },
  "2w": { days: 14 },
  "1m": { months: 1 },
  "3m": { months: 3 },
  "6m": { months: 6 },
};

function dateToInputValue(date) {
  return date.toISOString().slice(0, 10);
}

function getRangeStartDate(endDateValue, rangeKey) {
  const range = QUICK_RANGES[rangeKey];
  if (!range) {
    return null;
  }

  const endDate = new Date(`${endDateValue}T00:00:00`);
  const startDate = new Date(endDate);

  if (range.days) {
    startDate.setDate(startDate.getDate() - range.days);
  }

  if (range.months) {
    startDate.setMonth(startDate.getMonth() - range.months);
  }

  return dateToInputValue(startDate);
}

export default function App() {
  const [fechaInicio, setFechaInicio] = useState(DEFAULT_START_DATE);
  const [fechaFin, setFechaFin] = useState(DEFAULT_END_DATE);
  const [manualRange, setManualRange] = useState({
    fechaInicio: DEFAULT_START_DATE,
    fechaFin: DEFAULT_END_DATE,
  });
  const [quickRange, setQuickRange] = useState("manual");
  const [portfolioId, setPortfolioId] = useState("1");
  const [visiblePortfolioIds, setVisiblePortfolioIds] = useState(["1", "2"]);
  const [valueData, setValueData] = useState(null);
  const [weightsData, setWeightsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [valueResponse, weightsResponse] = await Promise.all([
        fetchPortfolioValue({ fechaInicio, fechaFin }),
        fetchPortfolioWeights({ fechaInicio, fechaFin, portfolioId }),
      ]);

      setValueData(valueResponse);
      setWeightsData(weightsResponse);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function loadWeights(nextPortfolioId) {
    setLoading(true);
    setError("");

    try {
      const weightsResponse = await fetchPortfolioWeights({
        fechaInicio,
        fechaFin,
        portfolioId: nextPortfolioId,
      });
      setWeightsData(weightsResponse);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  function handleQuickRangeChange(event) {
    const nextRange = event.target.value;
    setQuickRange(nextRange);

    if (nextRange === "manual") {
      setFechaInicio(manualRange.fechaInicio);
      setFechaFin(manualRange.fechaFin);
      return;
    }

    const nextStartDate = getRangeStartDate(fechaFin, nextRange);
    if (nextStartDate) {
      setFechaInicio(nextStartDate);
    }
  }

  function handleEndDateChange(event) {
    const nextEndDate = event.target.value;
    setFechaFin(nextEndDate);

    if (quickRange === "manual") {
      setManualRange((currentRange) => ({
        ...currentRange,
        fechaFin: nextEndDate,
      }));
      return;
    }

    const nextStartDate = getRangeStartDate(nextEndDate, quickRange);
    if (nextStartDate) {
      setFechaInicio(nextStartDate);
    }
  }

  function handleVisiblePortfolioToggle(portfolioIdToToggle) {
    setVisiblePortfolioIds((currentIds) => {
      if (currentIds.includes(portfolioIdToToggle)) {
        return currentIds.length === 1 ? currentIds : currentIds.filter((id) => id !== portfolioIdToToggle);
      }

      return [...currentIds, portfolioIdToToggle].sort();
    });
  }

  function handleCompositionPortfolioChange(event) {
    const nextPortfolioId = event.target.value;
    setPortfolioId(nextPortfolioId);
    loadWeights(nextPortfolioId);
  }

  useEffect(() => {
    loadData();
  }, []);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Portfolio analytics</p>
          <h1>Comparacion de portafolios</h1>
        </div>
        <div className="status-pill">{loading ? "Cargando" : "Listo"}</div>
      </header>

      <section className="toolbar" aria-label="Filtros">
        <label>
          Fecha inicio
          <input
            type="date"
            value={fechaInicio}
            onChange={(event) => {
              setQuickRange("manual");
              setFechaInicio(event.target.value);
              setManualRange({
                fechaInicio: event.target.value,
                fechaFin,
              });
            }}
          />
        </label>

        <label>
          Fecha fin
          <input type="date" value={fechaFin} onChange={handleEndDateChange} />
        </label>

        <label>
          Rango
          <select value={quickRange} onChange={handleQuickRangeChange}>
            <option value="manual">Manual</option>
            <option value="5d">Ultimos 5 dias</option>
            <option value="2w">Ultimas 2 semanas</option>
            <option value="1m">Ultimo mes</option>
            <option value="3m">Ultimos 3 meses</option>
            <option value="6m">Ultimos 6 meses</option>
          </select>
        </label>

        <fieldset className="portfolio-toggle-group">
          <legend>Portafolios</legend>
          <label>
            <input
              type="checkbox"
              checked={visiblePortfolioIds.includes("1")}
              onChange={() => handleVisiblePortfolioToggle("1")}
            />
            Portafolio 1
          </label>
          <label>
            <input
              type="checkbox"
              checked={visiblePortfolioIds.includes("2")}
              onChange={() => handleVisiblePortfolioToggle("2")}
            />
            Portafolio 2
          </label>
        </fieldset>

        <button type="button" onClick={loadData} disabled={loading}>
          Consultar
        </button>
      </section>

      {error ? <div className="error-box">{error}</div> : null}

      <section className="chart-grid">
        <article className="chart-panel">
          <div className="chart-header">
            <h2>Valor total</h2>
            <span>Vt</span>
          </div>
          <PortfolioValueChart data={valueData} visiblePortfolioIds={visiblePortfolioIds} />
        </article>

        <article className="chart-panel">
          <div className="chart-header">
            <h2>Composicion (Weights)</h2>
            <div className="chart-actions">
              <label>
                Portafolio
                <select value={portfolioId} onChange={handleCompositionPortfolioChange}>
                  <option value="1">Portafolio 1</option>
                  <option value="2">Portafolio 2</option>
                </select>
              </label>
            </div>
          </div>
          <PortfolioWeightsChart data={weightsData} />
        </article>
      </section>
    </main>
  );
}
