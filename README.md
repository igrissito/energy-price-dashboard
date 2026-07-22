# energy-price-dashboard

A small dashboard for Austrian day-ahead electricity prices, powered by the free
[aWATTar](https://www.awattar.at/en/hilfe/api-strompreise) market data API (no API
key required).

- **Backend:** FastAPI, fetches hourly prices from aWATTar and exposes them as JSON.
- **Frontend:** a single static HTML page (served by FastAPI itself) with a bar
  chart of hourly prices, cheapest upcoming hours highlighted in green.

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /prices` | All hourly prices aWATTar currently publishes (today, plus tomorrow once it's out, usually published ~14:00 CET). Each entry has `start`/`end` (ISO 8601, UTC), `price_eur_mwh`, and `price_ct_kwh`. |
| `GET /cheapest-hours?n=3` | The `n` cheapest hours among those still **upcoming** (i.e. not yet elapsed), sorted chronologically. `n` defaults to 3 and must be between 1 and 48. |
| `GET /` | The dashboard frontend (static page in `static/index.html`). |

Example:

```
GET /cheapest-hours?n=3
[
  { "start": "2026-07-22T12:00:00+00:00", "end": "2026-07-22T13:00:00+00:00", "price_eur_mwh": 73.23, "price_ct_kwh": 7.323 },
  { "start": "2026-07-23T09:00:00+00:00", "end": "2026-07-23T10:00:00+00:00", "price_eur_mwh": 74.92, "price_ct_kwh": 7.492 },
  { "start": "2026-07-23T10:00:00+00:00", "end": "2026-07-23T11:00:00+00:00", "price_eur_mwh": 48.24, "price_ct_kwh": 4.824 }
]
```

## Setup

You need Python 3.10+ (this was built and tested with the `py` launcher on
Windows). Either reuse an existing virtual environment that already has
`fastapi`, `uvicorn`, and `requests` installed, or create a fresh one:

```powershell
# from the project root
py -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

If you'd rather reuse an existing venv (e.g. one at `C:\Users\you\venv`), just
make sure it has the packages in `requirements.txt` installed:

```powershell
C:\Users\you\venv\Scripts\pip install -r requirements.txt
```

## Running the app

```powershell
# using a project-local venv
.venv\Scripts\python -m uvicorn app.main:app --reload

# or using an existing venv directly
C:\Users\you\venv\Scripts\python -m uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000** in a browser for the dashboard, or hit the
JSON endpoints directly at `http://127.0.0.1:8000/prices` and
`http://127.0.0.1:8000/cheapest-hours?n=3`.

`--reload` is handy during development (auto-restarts on code changes); drop it
for a plain run.

## Project layout

```
app/
  main.py      # FastAPI app: routes + static file mount
  awattar.py   # aWATTar API client, price formatting, cheapest-hours logic
static/
  index.html   # frontend: fetches /prices and /cheapest-hours, renders an SVG bar chart
requirements.txt
```

## Notes

- Prices are converted from the aWATTar unit (EUR/MWh) to the more commonly
  quoted ct/kWh (divide by 10) alongside the original EUR/MWh value.
- aWATTar only publishes a rolling window of prices (today, and tomorrow once
  published) — there's no historical query in this v1.
- The frontend is a single dependency-free HTML file (no build step, no CDN
  libraries) so `static/index.html` can be opened and edited directly.
