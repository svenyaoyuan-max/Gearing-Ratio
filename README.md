# Gearing Ratio Analyser

A web app that calculates the gearing ratio (total financial debt ÷ total equity)
for Chinese A-share / B-share listed companies, using live data from CNInfo and
Sina Finance. Auto-detects company type (standard, bank, securities, insurance)
and applies the appropriate debt definition.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (free)

Hosted on [Streamlit Community Cloud](https://streamlit.io/cloud).
Main file: `app.py`. No user registration required to use the app.

## Files

- `app.py` — Streamlit UI
- `gearing_ratio.py` — data-fetching functions (CNInfo profile + Sina balance sheet)
- `requirements.txt` — Python dependencies
- `.streamlit/config.toml` — theme / server config
