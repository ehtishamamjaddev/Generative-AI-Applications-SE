# Reflection: Lab 03

## What worked well
- Structuring API responses with standard HTTP status codes (200, 400, 409) matched RESTful best practices.
- Generating UUIDs provided strong data tracing.

## Challenges faced
- Implementing an efficient duplicate check without overwhelming the backend sheet API.

## How would you fix it
- Used exact string matching or limited the search span within the sheet to recent entries to speed up the check.

## Production considerations
- A real database (like PostgreSQL or MongoDB) should be used instead of Google Sheets for large-scale duplicate checks.
- API documentation must be kept in sync with the webhook configuration.

## Key learnings
- Defensive API design.
- The importance of unambiguous HTTP status codes in automated systems.
