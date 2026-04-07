# Static Site Browsing (No Connection Refused)

Use these scripts to reliably browse any local static deploy (HTML/CSS/JS) without losing the server.

## Start a site

```bash
bash shared/tools/serve_static_site.sh "/absolute/path/to/site" 8099 127.0.0.1
```

Important: Replace `/absolute/path/to/site` with the real folder path.

Example for Ziyada deploy extract:

```bash
bash shared/tools/serve_static_site.sh \
  "projects/ziyada-system/.tmp/zip_check_695d3ef_v2" \
  8099 \
  127.0.0.1
```

The script provides:
- PID tracking in `/tmp`
- Health check before declaring success
- Ready URLs (`/`, `index.html`, `ar.html` when present)
- Clear error if port is already in use

## Stop a managed site

```bash
bash shared/tools/stop_static_site.sh "/absolute/path/to/site" 8099 127.0.0.1
```

## Recommended workflow for any project

1. Extract/copy the deploy to a known folder.
2. Start it with `serve_static_site.sh`.
3. Open the printed URL in browser.
4. Stop it with `stop_static_site.sh` when done.

This pattern prevents the common `ERR_CONNECTION_REFUSED` issue caused by missing/terminated local servers.
