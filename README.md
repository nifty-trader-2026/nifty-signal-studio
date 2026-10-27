# Nifty Signal Studio — Free demo website

This is a **practice website**, not live trading software. The data is **synthetic**, not real historical prices. No Groww API, login, credit card or AI API key is required. The app **cannot trade**.

## For non-technical users: publish with Streamlit Community Cloud

You'll need a free GitHub account and a free Streamlit Community Cloud account. The free hosting plan is subject to provider limits and terms. Publishing a public Streamlit app means anyone with its URL can view the demonstration dashboard. **Do not upload passwords, API keys, Groww access tokens or personal portfolio data to this repository.**

1. Visit https://github.com/ and sign up or sign in.
2. Click **+** (top-right) > **New repository**. Give it a name like `nifty-signal-studio`, choose **Public**, and click **Create repository**.
3. On the repository page, click **uploading an existing file** or **Add file > Upload files**.
4. Unzip the downloaded project on your computer. Upload **app.py**, **engine.py**, and **requirements.txt** from inside the extracted folder (upload these three files to the top level of the repository). Commit changes.
5. Go to https://share.streamlit.io/ and sign in with GitHub.
6. Select **Create app** > **Yup, I have an app** (wording may change), select your GitHub repository, set the main file path to `app.py` and deploy.
7. Open the new `*.streamlit.app` URL. Use the left menu to open the scanner, stock details, and risk calculator.

If you prefer not to publish anything, you can run this on your own computer later, but that would need a Python installation.

## What does each file do?
- `app.py`: Website user interface and CSV download.
- `engine.py`: Artificial sample prices and deterministic signal logic.
- `requirements.txt`: Software packages installed by Streamlit.

## Initial sample rules (not validated trading recommendations)
- Last close above 50-day simple moving average.
- 50-day SMA above 200-day SMA.
- 14-day RSI between 50 and 70.
- Last volume above the previous 20-day average volume.
- Last close above the previous 20-day high.

If all five pass, show BUY CANDIDATE; otherwise WAIT. Scores are percentage of rules satisfied, **not probability of profit**. No sell/exit recommendations are generated, as this demo has no position records. The data ends on October 26, 2026 for consistency and is not live.

## Future real-market version
Real signals require accurate, properly licensed NSE stock data; updated Nifty 50 membership; handling adjusted prices, missing data and corporate actions; trustworthy backtesting; and risk checks. Groww data access might incur charges. An optional OpenAI/Anthropic API could *explain* rules but should not change deterministic decisions or place trades.
