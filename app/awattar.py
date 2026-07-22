"""Client for the aWATTar Austria day-ahead market price API.

Docs: https://www.awattar.at/en/hilfe/api-strompreise (no API key required).
"""

from datetime import datetime, timezone

import requests

AWATTAR_URL = "https://api.awattar.at/v1/marketdata"


class AwattarError(Exception):
    """Raised when the aWATTar API can't be reached or returns bad data."""


def _to_iso(ms_timestamp: int) -> str:
    return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc).isoformat()


def _format_entry(entry: dict) -> dict:
    price_eur_mwh = entry["marketprice"]
    return {
        "start": _to_iso(entry["start_timestamp"]),
        "end": _to_iso(entry["end_timestamp"]),
        # aWATTar reports Eur/MWh; divide by 10 to get the more familiar ct/kWh
        # (Eur/MWh -> Eur/kWh is /1000, then ct is *100, net /10).
        "price_eur_mwh": price_eur_mwh,
        "price_ct_kwh": round(price_eur_mwh / 10, 3),
    }


def fetch_prices() -> list[dict]:
    """Fetch hourly day-ahead prices from aWATTar, oldest first."""
    try:
        response = requests.get(AWATTAR_URL, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise AwattarError(f"Could not fetch prices from aWATTar: {exc}") from exc

    entries = payload.get("data", [])
    formatted = [_format_entry(e) for e in entries]
    formatted.sort(key=lambda e: e["start"])
    return formatted


def get_cheapest_hours(n: int = 3) -> list[dict]:
    """Return the n cheapest hours among those still upcoming (not yet elapsed).

    Results are sorted chronologically (not by price) so they read naturally
    on a timeline / bar chart.
    """
    prices = fetch_prices()
    now = datetime.now(timezone.utc)
    upcoming = [p for p in prices if datetime.fromisoformat(p["end"]) > now]
    cheapest = sorted(upcoming, key=lambda p: p["price_eur_mwh"])[:n]
    cheapest.sort(key=lambda p: p["start"])
    return cheapest
