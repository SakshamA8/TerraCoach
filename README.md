# EcoCart AI

EcoCart AI is an AI-powered grocery sustainability platform that analyzes receipt purchases, estimates product-level carbon footprints, recommends lower-emission swaps, and guides shoppers through a 3D supermarket to make greener choices. Built for HackDuke 2026.

## Run locally

The app listens on port **1970**.

- **Docker:** `docker compose up --build`, then open [http://localhost:1970](http://localhost:1970).
- **Flask:** `python app.py` — same URL. In the Auth0 application settings, allow callback **http://localhost:1970/callback** (and set `AUTH0_REDIRECT_URI` in `.env` to match).
