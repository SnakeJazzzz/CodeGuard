# Web Application Layer

This directory contains the Flask web application that provides the user interface for CodeGuard.

## Files

### `app.py`
Flask application initialization and configuration.

**Responsibilities**:
- Create and configure Flask application instance
- Register blueprints and routes
- Configure session management
- Set up error handlers
- Initialize database connection
- Configure file upload settings

**Key Configuration**:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = '/app/data/uploads'
app.config['RESULTS_FOLDER'] = '/app/data/results'
app.config['ALLOWED_EXTENSIONS'] = {'.py'}
```

### `routes.py`
HTTP route handlers and request processing.

**Routes**:
- `GET /` - Home page with upload form
- `POST /upload` - Handle file upload and initiate analysis
- `GET /results/<job_id>` - Display analysis results
- `GET /download/<job_id>` - Download JSON report
- `GET /health` - Health check endpoint for Docker

**Request Flow**:
1. User uploads files via form
2. Files validated and saved to uploads directory
3. Analysis job created with unique ID
4. Detection engine processes files
5. Results stored in database and JSON file
6. User redirected to results page

### `forms.py`
Form validation and file upload handling using Flask-WTF.

**Forms**:
- `UploadForm` - Multi-file upload with validation
  - Validates file extensions (.py only)
  - Checks file size limits
  - Ensures minimum 2 files uploaded
  - Validates Python syntax

**Validation Rules**:
```python
- File extension: .py only
- File size: ≤16MB per file
- Minimum files: 2
- Maximum files: 100
- Syntax: Must be valid Python
```

### `file_handler.py`
File upload management, validation, and storage.

**Functions**:
- `save_uploaded_files(files: List[FileStorage]) -> List[str]`
  - Saves files to upload directory
  - Generates unique filenames to prevent collisions
  - Returns list of saved file paths

- `validate_python_file(filepath: str) -> bool`
  - Validates Python syntax using `ast.parse()`
  - Returns True if valid, False otherwise

- `cleanup_old_uploads(hours: int = 24)`
  - Removes upload files older than specified hours
  - Prevents disk space exhaustion

- `get_file_stats(filepath: str) -> Dict`
  - Returns file statistics (size, lines, etc.)

## Web Interface Features

### Upload Page (`/`)
- Drag-and-drop file upload
- Multiple file selection
- File list preview before submission
- Progress indicator during upload
- Client-side validation

### Results Page (`/results/<job_id>`)
- File pair comparison matrix
- Similarity scores visualization
- Color-coded plagiarism indicators
  - Red: Plagiarism detected (confidence ≥50%)
  - Green: No plagiarism (confidence <50%)
- Individual detector scores
- Confidence percentage
- Detailed breakdown for each pair
- Download JSON report button

### Error Handling
- 400 Bad Request: Invalid file uploads
- 404 Not Found: Job ID doesn't exist
- 413 Request Entity Too Large: File size exceeded
- 500 Internal Server Error: Processing failures

## Templates Integration

The web layer uses Jinja2 templates from `templates/`:
- `base.html` - Base template with navigation
- `index.html` - Upload form page
- `results.html` - Analysis results display
- `error.html` - Error message display

## Static Assets

References static files from `static/`:
- CSS: `static/css/main.css`, `static/css/upload.css`, `static/css/results.css`
- JavaScript: `static/js/upload.js`, `static/js/results.js`, `static/js/progress.js`
- Images: `static/images/logo.png`, `static/images/favicon.ico`

## Security Considerations

1. **File Validation**:
   - Extension whitelist (.py only)
   - MIME type verification
   - Syntax validation before processing

2. **Path Traversal Prevention**:
   - Secure filename generation
   - Restricted upload directory access
   - No user-controlled paths

3. **Resource Limits**:
   - File size limits (16MB)
   - Upload rate limiting
   - Concurrent analysis limits

4. **Input Sanitization**:
   - Escape user inputs in templates
   - Validate job IDs (alphanumeric only)
   - CSRF protection via Flask-WTF

## API Response Format

### Success Response
```json
{
  "status": "success",
  "job_id": "20251105_143022",
  "message": "Analysis completed",
  "results_url": "/results/20251105_143022"
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Invalid file format",
  "errors": ["File 'test.txt' is not a Python file"]
}
```

## Development

### Running Locally
```bash
# Set environment variables
export FLASK_APP=src.web.app
export FLASK_ENV=development

# Run development server
flask run --host=0.0.0.0 --port=5000
```

### Testing
```bash
# Test routes
pytest tests/integration/test_api_endpoints.py

# Test with coverage
pytest tests/integration/test_api_endpoints.py --cov=src.web
```

## Configuration

Environment variables:
- `FLASK_ENV` - development/production
- `FLASK_SECRET_KEY` - Session encryption key
- `UPLOAD_FOLDER` - Upload directory path
- `RESULTS_FOLDER` - Results storage path
- `MAX_CONTENT_LENGTH` - Max upload size in bytes

## Dependencies

- Flask 3.0+ - Web framework
- Werkzeug - WSGI utilities and file handling
- Jinja2 - Template engine
- Flask-WTF - Form validation (optional)
