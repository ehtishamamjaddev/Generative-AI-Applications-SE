# Lab 02: Google Sheets & LLM Integration

## 🎯 Objective
Integrate external APIs and Large Language Models (LLMs) into workflows to generate and filter content based on specific criteria.

## 🛠️ Implementation Details
- **Google Sheets Trigger:** Monitors a spreadsheet for new rows containing topics or prompts.
- **AI Content Generation:** Connects to Groq (using llama3-8b) to generate social media posts based on the spreadsheet input.
- **Quality Gate:** Implements a validation step ensuring generated posts have a word count ≥ 80 and include at least one hashtag.
- **Conditional Routing:** Approved posts are saved; rejected posts are logged into a separate "Rejections" sheet.

## 🧪 Test Results
- ✅ Switched successfully from Gemini to Groq dynamically due to rate limits.
- ✅ Posts under 80 words are correctly identified and routed to the rejection sheet.
- ✅ Approved content flows successfully.
