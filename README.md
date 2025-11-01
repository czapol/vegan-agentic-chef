# Vegan Chef (Streamlit)

Simple Streamlit agent that suggests easy vegan recipes based on a short prompt.

## Quick start
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run veganchef.py   # or veganchefhtml.py
```

## Dev notes
- Keep secrets in `.streamlit/secrets.toml` (not committed).
- Only `veganchef*` files are tracked.
