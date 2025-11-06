# API Documentation

REST API documentation for the CodeGuard web application.

## Files

- `endpoints.md` - Complete API endpoint reference
- `request-examples.md` - Example requests and responses
- `error-codes.md` - Error codes and handling

## Base URL

```
http://localhost:5000
```

## Endpoints Overview

### Upload Files

```http
POST /upload
Content-Type: multipart/form-data

Returns: 302 Redirect or JSON response with job_id
```

### View Results

```http
GET /results/<job_id>

Returns: HTML page with analysis results
```

### Download Report

```http
GET /download/<job_id>

Returns: JSON file with complete analysis data
```

### Health Check

```http
GET /health

Returns: JSON with system status
```

## Authentication

Currently no authentication required (local deployment).

## Rate Limiting

No rate limiting (single-user application).

## Example Workflow

1. Upload files via POST /upload
2. Receive job_id in response
3. View results at /results/<job_id>
4. Download JSON at /download/<job_id>

See `request-examples.md` for detailed examples.
