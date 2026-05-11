# Reflection: Lab 01

## What worked well
- Visualizing the data flow natively in n8n made debugging input structures incredibly easy.
- The webhook node handled HTTP request parsing effortlessly.

## Challenges faced
- Configuring the exact timezone and cron expressions for the Office Hours task.
- Ensuring the IF node properly validated nested JSON structures.

## How would you fix it
- Used explicit time nodes and tested cron expressions using external tools (like crontab.guru) before applying them.

## Production considerations
- In a production environment, webhooks should be secured with authentication headers (e.g., Bearer tokens).
- Error trigger nodes should be added to catch and report global workflow failures.

## Key learnings
- Event-driven architecture concepts.
- Basic API creation and conditional routing without traditional programming.
