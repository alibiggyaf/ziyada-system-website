# Local Data Ownership

This directory stores the website's local, self-owned application data.

Files:
- `blog-posts.json` — Admin-managed blog content created through the local API
- `case-studies.json` — Admin-managed case studies
- `leads.json` — Contact/proposal submissions
- `bookings.json` — Meeting requests and statuses
- `subscribers.json` — Newsletter signups
- `reset-tokens.json` — Short-lived credential reset records
- `outbox.json` — Email messages queued locally when SMTP is not configured

Notes:
- Public blog and case-study pages still have source-controlled fallback content in `src/pages/blogContent.jsx` and `src/pages/Cases.jsx`.
- Once records exist here, the local API serves them to the website and admin dashboard.
- Keep this directory under your control for full ownership of website data.
