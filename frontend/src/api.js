const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function apiGet(path, params) {
  const url = new URL(`${API_BASE_URL}${path}`);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, value);
    }
  });

  const response = await fetch(url);
  if (!response.ok) {
    const details = await response.text();
    throw new Error(details || "API request failed");
  }

  return response.json();
}

export function fetchPortfolioValue({ fechaInicio, fechaFin }) {
  return apiGet("/api/portfolios/value/", {
    fecha_inicio: fechaInicio,
    fecha_fin: fechaFin,
  });
}

export function fetchPortfolioWeights({ fechaInicio, fechaFin, portfolioId }) {
  return apiGet("/api/portfolios/weights/", {
    fecha_inicio: fechaInicio,
    fecha_fin: fechaFin,
    portfolio_id: portfolioId,
  });
}
