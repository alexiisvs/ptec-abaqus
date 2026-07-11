import { useEffect, useState } from "react";

import { fetchPortfolioValue, fetchPortfolioWeights } from "./api";
import PortfolioValueChart from "./components/PortfolioValueChart";
import PortfolioWeightsChart from "./components/PortfolioWeightsChart";

const DEFAULT_START_DATE = "2022-02-15";
const DEFAULT_END_DATE = "2023-02-16";

export default function App() {
  const [fechaInicio, setFechaInicio] = useState(DEFAULT_START_DATE);
  const [fechaFin, setFechaFin] = useState(DEFAULT_END_DATE);
  const [portfolioId, setPortfolioId] = useState("1");
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
          <input type="date" value={fechaInicio} onChange={(event) => setFechaInicio(event.target.value)} />
        </label>

        <label>
          Fecha fin
          <input type="date" value={fechaFin} onChange={(event) => setFechaFin(event.target.value)} />
        </label>

        <label>
          Weights
          <select value={portfolioId} onChange={(event) => setPortfolioId(event.target.value)}>
            <option value="1">Portafolio 1</option>
            <option value="2">Portafolio 2</option>
          </select>
        </label>

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
          <PortfolioValueChart data={valueData} />
        </article>

        <article className="chart-panel">
          <div className="chart-header">
            <h2>Composicion</h2>
            <span>wi,t</span>
          </div>
          <PortfolioWeightsChart data={weightsData} />
        </article>
      </section>
    </main>
  );
}
