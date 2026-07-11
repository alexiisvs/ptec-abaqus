# PTEC Abaqus

## Stack

- Backend: Django + Django REST Framework
- Base de datos: PostgreSQL via Docker Compose
- Frontend: React + Vite
- Gráficos: ECharts
- ETL: management command de Django
- Fuente de datos: `data/datos.xlsx`

## Setup

### Backend

```bash
docker compose up -d db
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python backend/manage.py migrate
python backend/manage.py load_portfolio_data data/datos.xlsx
python backend/manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

El frontend queda disponible en `http://localhost:5173` y consume la API en
`http://localhost:8000`.
