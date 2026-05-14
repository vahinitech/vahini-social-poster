# vahini-social-poster

A lightweight local social media posting dashboard built with Flask, HTMX, Jinja2, and SQLite.

## Features

- minimal dashboard with connected account, recent post, and draft summaries
- compose workflow with HTMX-powered autosave, draft saving, and async publish actions
- settings page for connect/disconnect account flows with OAuth skeleton support
- modular service layer for LinkedIn, X/Twitter, Facebook Pages, and Instagram Business
- encrypted token storage in SQLite and local image uploads
- cross-platform local startup with optional browser auto-open

## Project structure

```text
app/
├── app.py
├── config.py
├── database/
├── models/
├── routes/
├── services/
├── static/
└── templates/
```

## Local setup

1. Create a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Optional environment variables:

   - `VAHINI_SECRET_KEY`
   - `VAHINI_DATABASE_PATH`
   - `VAHINI_UPLOAD_FOLDER`
   - `VAHINI_AUTO_OPEN_BROWSER`
   - `VAHINI_HOST`
   - `VAHINI_PORT`
   - `{PLATFORM}_CLIENT_ID`, `{PLATFORM}_CLIENT_SECRET`, `{PLATFORM}_AUTHORIZE_URL`, `{PLATFORM}_TOKEN_URL`, `{PLATFORM}_API_BASE_URL`

4. Start the app:

   ```bash
   python -m app.app
   ```

5. Open `http://127.0.0.1:5000` if the browser does not open automatically.

## Testing

Run the starter test suite with:

```bash
python -m unittest discover -s tests
```

## Notes

- OAuth routes are wired for future real API credentials, but default to safe local placeholder connections until credentials are provided.
- Posts and tokens are stored locally in SQLite for a single-user internal workflow.
