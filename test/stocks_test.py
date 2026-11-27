from unittest.mock import Mock

import pytest
import requests

from app import stocks


def test_sample_report_normalizes_and_sorts_prices():
    report = stocks.get_stock_report(" aapl ")
    assert report["symbol"] == "AAPL"
    assert "Historical monthly prices" in report["source"]
    assert len(report["prices"]) == 30
    dates = [row["date"] for row in report["prices"]]
    assert dates == sorted(dates)
    assert report["prices"][-1] == {"date": "2010-03-01", "close": 223.02}


@pytest.mark.parametrize("symbol", ["", "AAPL<script>", "NOTATICKER"])
def test_invalid_or_unknown_symbols_are_rejected(symbol):
    with pytest.raises(stocks.UnknownSymbol):
        stocks.get_stock_report(symbol)


def test_api_report_reuses_recent_success(monkeypatch):
    response = Mock()
    response.json.return_value = {
        "Time Series (Daily)": {
            "2026-02-05": {"4. close": "103.25"},
            "2026-02-04": {"4. close": "100.00"},
        }
    }
    get = Mock(return_value=response)
    monkeypatch.setattr(stocks.requests, "get", get)
    monkeypatch.setattr(stocks, "monotonic", lambda: 900)
    stocks.fetch_daily_prices.cache_clear()

    for _ in range(2):
        report = stocks.get_stock_report("BRK.B", api_key="test-key")
        assert report["prices"] == [
            {"date": "2026-02-04", "close": 100.00},
            {"date": "2026-02-05", "close": 103.25},
        ]

    get.assert_called_once_with(
        stocks.API_URL,
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": "BRK.B",
            "outputsize": "compact",
            "apikey": "test-key",
        },
        timeout=8,
    )
    stocks.fetch_daily_prices.cache_clear()


@pytest.mark.parametrize("payload, error", [
    ({"Error Message": "Invalid API call"}, stocks.UnknownSymbol),
    ({"Information": "API limit reached"}, stocks.StockDataError),
    ({"Time Series (Daily)": {"2026-02-05": {"4. close": "NaN"}}}, stocks.StockDataError),
])
def test_provider_error_responses(payload, error):
    with pytest.raises(error):
        stocks.parse_daily_prices(payload, "INVALID")


def test_api_timeout_is_reported(monkeypatch):
    monkeypatch.setattr(stocks.requests, "get", Mock(side_effect=requests.Timeout))
    with pytest.raises(stocks.StockDataError, match="could not be reached"):
        stocks.get_stock_report("IBM", api_key="test-timeout-key")
