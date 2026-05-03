# API Documentation: Student Q&A System

## Overview
This API allows students to submit questions to the Q&A system. It includes validation, duplicate checking, and automated logging.

## Endpoint
**POST** `/webhook/student-qa`

### Headers
- `Content-Type: application/json`

### Request Body
```json
{
  "student_name": "string (Required, Alpha characters only)",
  "question": "string (Required, Minimum 10 characters)",
  "course_id": "string (Optional)"
}
```

### Responses

#### 200 OK (Success)
Returned when the question is valid, not a duplicate, and successfully recorded.
```json
{
  "status": "success",
  "submission_id": "uuid",
  "message": "Question successfully submitted.",
  "timestamp": "ISO-8601"
}
```

#### 400 Bad Request (Validation Error)
Returned if the `student_name` is invalid or `question` is under 10 characters.
```json
{
  "status": "error",
  "error_type": "VALIDATION_FAILED",
  "message": "Question must be at least 10 characters long."
}
```

#### 409 Conflict (Duplicate)
Returned if the exact same question was recently submitted.
```json
{
  "status": "error",
  "error_type": "DUPLICATE_ENTRY",
  "message": "This question has already been submitted."
}
```
