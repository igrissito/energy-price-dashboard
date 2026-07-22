from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from app.awattar import AwattarError, fetch_prices, get_cheapest_hours

app = FastAPI(title="Austrian Electricity Price Dashboard")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/prices")
def prices():
    """All available hourly day-ahead prices (today, plus tomorrow once published)."""
    try:
        return fetch_prices()
    except AwattarError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/cheapest-hours")
def cheapest_hours(n: int = Query(3, ge=1, le=48, description="How many cheapest hours to return")):
    """The n cheapest upcoming hours, sorted chronologically."""
    try:
        return get_cheapest_hours(n)
    except AwattarError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# Mounted last and at "/" so it never shadows the API routes above: FastAPI
# matches routes in the order they were added, and the specific /prices and
# /cheapest-hours routes are registered before this catch-all static mount.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
