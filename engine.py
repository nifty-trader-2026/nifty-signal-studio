"""Educational sample-data screening logic; does not connect to brokers."""
import numpy as np
import pandas as pd

STOCKS = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "BHARTIARTL", "ITC", "LT", "SBIN", "AXISBANK", "KOTAKBANK", "HINDUNILVR", "BAJFINANCE", "MARUTI", "SUNPHARMA"]


def make_demo_data():
    """Synthetic—not actual exchange prices. Reproducible on every run."""
    frames = []
    dates = pd.bdate_range(end="2026-10-26", periods=330)
    for idx, ticker in enumerate(STOCKS):
        rng = np.random.default_rng(2000 + idx)
        drift = 0.0007 if idx % 3 == 0 else (0.0003 if idx % 3 == 1 else -0.0002)
        noise = rng.normal(drift, 0.014, len(dates))
        close = (450 + idx * 105) * np.exp(np.cumsum(noise))
        close = np.maximum(close, 1)
        open_ = close * (1 + rng.normal(0, 0.004, len(dates)))
        high = np.maximum(close, open_) * (1 + rng.uniform(0.001, .012, len(dates)))
        low = np.minimum(close, open_) * (1 - rng.uniform(0.001, .012, len(dates)))
        volume = rng.integers(200_000, 4_000_000, len(dates)).astype(int)
        frames.append(pd.DataFrame({"date": dates, "symbol": ticker, "open": open_, "high": high, "low": low, "close": close, "volume": volume}))
    return pd.concat(frames, ignore_index=True)


def _rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.fillna(50)


def evaluate(df):
    required = {"date", "symbol", "open", "high", "low", "close", "volume"}
    if not required.issubset(df.columns):
        raise ValueError("Missing columns: " + ", ".join(sorted(required - set(df.columns))))
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=list(required)).sort_values(["symbol", "date"])
    rows = []
    price_history = {}
    for symbol, g in df.groupby("symbol"):
        g = g.drop_duplicates("date", keep="last").sort_values("date").copy()
        if len(g) < 220 or (g[["open", "high", "low", "close"]] <= 0).any().any() or (g["volume"] < 0).any():
            continue
        g["sma50"] = g["close"].rolling(50).mean()
        g["sma200"] = g["close"].rolling(200).mean()
        g["rsi14"] = _rsi(g["close"])
        g["prev20_high"] = g["high"].shift(1).rolling(20).max()
        g["avg_volume20"] = g["volume"].shift(1).rolling(20).mean()
        current = g.iloc[-1]
        checks = {
            "Above SMA50": current["close"] > current["sma50"],
            "SMA50 above SMA200": current["sma50"] > current["sma200"],
            "RSI 50–70": 50 <= current["rsi14"] <= 70,
            "Volume above average": current["volume"] > current["avg_volume20"],
            "20-day breakout": current["close"] > current["prev20_high"],
        }
        score = sum(bool(c) for c in checks.values()) * 20
        signal = "BUY CANDIDATE" if score == 100 else "WAIT"
        explanations = [name + (": pass" if passed else ": not met") for name, passed in checks.items()]
        rows.append({"symbol": symbol, "date": current["date"].strftime("%Y-%m-%d"), "close": round(float(current["close"]), 2), "signal": signal, "score": score, "rsi14": round(float(current["rsi14"]), 1), "sma50": round(float(current["sma50"]), 2), "sma200": round(float(current["sma200"]), 2), "reason": "; ".join(explanations)})
        price_history[symbol] = g
    return pd.DataFrame(rows).sort_values(["score", "symbol"], ascending=[False, True]).reset_index(drop=True), price_history


def size_position(capital, risk_pct, entry, stop, max_allocation_pct=20):
    if capital <= 0 or entry <= 0 or stop < 0 or stop >= entry:
        return None
    shares = int(min((capital * risk_pct / 100) / (entry - stop), (capital * max_allocation_pct / 100) / entry))
    return {"shares": shares, "investment": shares * entry, "planned_loss": shares * (entry-stop), "risk_budget": capital * risk_pct / 100}
