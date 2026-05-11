# Lab 01: n8n Workflow Automation

## 🎯 Objective
Learn the fundamentals of workflow automation using n8n by building event-driven and time-scheduled processes without writing extensive code.

## 🛠️ Implementation Details
- **Task 1: Webhook-Based Mini API** - Implemented a webhook node that receives JSON payloads, validates the input using IF nodes, and conditionally returns HTTP 200 (Success) or 400 (Bad Request).
- **Task 2: Scheduled Office-Hours Logger** - Set up a Cron trigger to run Monday-Friday at 09:00 AM, checking conditions and logging timestamps.
- **Task 3: File Operations** - Persisted workflow outputs or logs to the local file system.

## 🧪 Test Results
- ✅ Valid payloads return expected success messages.
- ✅ Invalid payloads successfully trigger the rejection branch.
- ✅ Scheduler correctly filters non-office hours.
