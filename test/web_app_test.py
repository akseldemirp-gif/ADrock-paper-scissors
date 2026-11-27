import pytest

from web_app import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-key", "ALPHAVANTAGE_API_KEY": ""})
    return app.test_client()


@pytest.mark.parametrize("path, content", [
    ("/", b"Play a round"),
    ("/home", b"Look up a stock"),
    ("/rps/form", b'<option value="scissors">'),
    ("/stocks/form", b'<input id="symbol"'),
])
def test_pages_render(client, path, content):
    response = client.get(path)
    assert response.status_code == 200
    assert content in response.data
    assert b"bootstrap" in response.data


def test_health_endpoint(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_rps_game_shows_result(client, monkeypatch):
    monkeypatch.setattr("web_app.routes.choice", lambda options: "scissors")
    response = client.post("/rps/play", data={"choice": "rock"})
    assert response.status_code == 200
    assert b"You win!" in response.data
    assert b"<dd>Rock</dd>" in response.data
    assert b"<dd>Scissors</dd>" in response.data


def test_invalid_rps_choice_redirects(client):
    response = client.post("/rps/play", data={"choice": "lizard"})
    assert response.status_code == 303
    assert response.location == "/rps/form"


def test_stocks_dashboard_has_price_rows_and_chart_data(client):
    response = client.post("/stocks/dashboard", data={"symbol": " aapl "})
    assert response.status_code == 200
    assert b"AAPL price history" in response.data
    assert b"<table" in response.data
    assert b'<canvas id="price-chart"' in response.data
    assert b'"close": 223.02' in response.data
    assert b"<td>2010-03-01</td>" in response.data


def test_bad_ticker_flashes_once_and_redirects_to_form(client):
    response = client.post("/stocks/dashboard", data={"symbol": "NOTATICKER"})
    assert response.status_code == 303
    assert response.location == "/stocks/form"

    form = client.get(response.location)
    assert b'role="alert"' in form.data
    assert b"No stock data found for NOTATICKER" in form.data
    assert b"No stock data found" not in client.get(response.location).data
