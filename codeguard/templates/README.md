# Templates

Jinja2 templates for the Flask web application.

## Files

### `base.html`
Base template with common layout structure.

**Includes**:
- HTML document structure
- Meta tags and favicon
- CSS includes
- Navigation header
- Footer
- JavaScript includes
- Content block for child templates

**Structure**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CodeGuard{% endblock %}</title>

    <!-- Favicon -->
    <link rel="icon" href="{{ url_for('static', filename='images/favicon.ico') }}">

    <!-- CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="container">
            <a href="/" class="logo">
                <img src="{{ url_for('static', filename='images/logo.png') }}" alt="CodeGuard">
            </a>
            <ul class="nav-links">
                <li><a href="/">Upload</a></li>
                <li><a href="/about">About</a></li>
            </ul>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 CodeGuard. Built for Academic Integrity.</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script src="{{ url_for('static', filename='js/utils.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### `index.html`
Homepage with file upload form.

**Extends**: `base.html`

**Features**:
- File upload form
- Drag-and-drop dropzone
- File selection button
- File requirements information
- Upload button

**Structure**:
```html
{% extends "base.html" %}

{% block title %}Upload Files - CodeGuard{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/upload.css') }}">
{% endblock %}

{% block content %}
<div class="upload-page">
    <h1>Code Plagiarism Detection</h1>
    <p class="subtitle">Upload Python files to analyze for plagiarism</p>

    <form method="POST" action="/upload" enctype="multipart/form-data" id="uploadForm">
        <!-- Dropzone -->
        <div class="upload-dropzone" id="dropzone">
            <div class="upload-icon">📁</div>
            <p class="upload-text">Drag and drop Python files here</p>
            <p class="upload-hint">or click to browse</p>
            <input type="file"
                   name="files"
                   id="fileInput"
                   multiple
                   accept=".py"
                   style="display: none;">
        </div>

        <!-- File List -->
        <div id="fileList" class="file-list"></div>

        <!-- Requirements -->
        <div class="upload-requirements">
            <h3>Requirements</h3>
            <ul>
                <li>Minimum 2 Python (.py) files</li>
                <li>Maximum 16MB per file</li>
                <li>Up to 100 files per batch</li>
            </ul>
        </div>

        <!-- Submit Button -->
        <button type="submit" class="btn btn-primary btn-large" id="uploadBtn">
            Analyze for Plagiarism
        </button>
    </form>

    <!-- Progress Indicator -->
    <div id="progressIndicator" class="progress-indicator" style="display: none;">
        <div class="progress-bar">
            <div class="progress-bar__fill"></div>
        </div>
        <p class="progress-percent">0%</p>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/upload.js') }}"></script>
<script src="{{ url_for('static', filename='js/progress.js') }}"></script>
{% endblock %}
```

### `results.html`
Analysis results display page.

**Extends**: `base.html`

**Features**:
- Job summary statistics
- Sorting and filtering controls
- Comparison results cards
- Similarity scores visualization
- Download JSON report button

**Structure**:
```html
{% extends "base.html" %}

{% block title %}Results - CodeGuard{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/results.css') }}">
{% endblock %}

{% block content %}
<div class="results-page">
    <h1>Analysis Results</h1>

    <!-- Summary -->
    <div class="results-summary">
        <div class="summary-card">
            <h3>Total Pairs Compared</h3>
            <p class="summary-value">{{ results|length }}</p>
        </div>
        <div class="summary-card">
            <h3>Plagiarism Detected</h3>
            <p class="summary-value summary-value--danger">
                {{ results|selectattr('is_plagiarized')|list|length }}
            </p>
        </div>
        <div class="summary-card">
            <h3>Average Confidence</h3>
            <p class="summary-value">
                {{ "%.1f"|format((results|map(attribute='confidence_score')|sum / results|length) * 100) }}%
            </p>
        </div>
    </div>

    <!-- Controls -->
    <div class="results-controls">
        <div class="control-group">
            <label for="sortBy">Sort by:</label>
            <select id="sortBy">
                <option value="confidence">Confidence</option>
                <option value="tokenSimilarity">Token Similarity</option>
                <option value="astSimilarity">AST Similarity</option>
                <option value="hashSimilarity">Hash Similarity</option>
            </select>
        </div>

        <div class="control-group">
            <label for="filterBy">Filter:</label>
            <select id="filterBy">
                <option value="all">All Results</option>
                <option value="plagiarized">Plagiarized Only</option>
                <option value="clean">Clean Only</option>
            </select>
        </div>

        <a href="/download/{{ job_id }}" class="btn btn-secondary">
            Download JSON Report
        </a>
    </div>

    <!-- Results List -->
    <div id="resultsContainer">
        {% for result in results %}
        <div class="result-card {% if result.is_plagiarized %}result-card--plagiarized{% else %}result-card--clean{% endif %}"
             data-confidence="{{ result.confidence_score }}"
             data-token="{{ result.token_similarity }}"
             data-ast="{{ result.ast_similarity }}"
             data-hash="{{ result.hash_similarity }}">

            <!-- Header -->
            <div class="result-header">
                <div class="result-files">
                    <code>{{ result.file1 }}</code>
                    <span class="vs">vs</span>
                    <code>{{ result.file2 }}</code>
                </div>

                <div class="result-status">
                    {% if result.is_plagiarized %}
                    <span class="badge badge--danger">Plagiarism Detected</span>
                    {% else %}
                    <span class="badge badge--success">Clean</span>
                    {% endif %}
                </div>
            </div>

            <!-- Confidence -->
            <div class="result-confidence">
                <h4>Confidence: {{ "%.1f"|format(result.confidence_score * 100) }}%</h4>
                <div class="confidence-bar">
                    <div class="confidence-bar__fill {% if result.confidence_score >= 0.8 %}confidence-bar__fill--high{% elif result.confidence_score >= 0.5 %}confidence-bar__fill--medium{% else %}confidence-bar__fill--low{% endif %}"
                         style="width: {{ result.confidence_score * 100 }}%">
                    </div>
                </div>
            </div>

            <!-- Similarity Scores -->
            <div class="similarity-scores">
                <div class="score-badge score-badge--token">
                    Token: {{ "%.1f"|format(result.token_similarity * 100) }}%
                </div>
                <div class="score-badge score-badge--ast">
                    AST: {{ "%.1f"|format(result.ast_similarity * 100) }}%
                </div>
                <div class="score-badge score-badge--hash">
                    Hash: {{ "%.1f"|format(result.hash_similarity * 100) }}%
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/results.js') }}"></script>
{% endblock %}
```

### `error.html`
Error page for displaying error messages.

**Extends**: `base.html`

**Features**:
- Error code display
- Error message
- Helpful suggestions
- Return to home link

**Structure**:
```html
{% extends "base.html" %}

{% block title %}Error - CodeGuard{% endblock %}

{% block content %}
<div class="error-page">
    <div class="error-container">
        <h1 class="error-code">{{ error_code|default('Error') }}</h1>
        <h2 class="error-message">{{ error_message|default('An error occurred') }}</h2>

        {% if error_details %}
        <div class="error-details">
            <h3>Details:</h3>
            <ul>
                {% for detail in error_details %}
                <li>{{ detail }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}

        <div class="error-actions">
            <a href="/" class="btn btn-primary">Return to Home</a>
        </div>
    </div>
</div>
{% endblock %}
```

## Jinja2 Features

### Template Inheritance
```html
{% extends "base.html" %}
```

### Blocks
```html
{% block content %}
    <!-- Content here -->
{% endblock %}
```

### Variables
```html
{{ variable_name }}
{{ variable|filter }}
```

### Filters
```html
{{ value|default('default') }}
{{ number|round(2) }}
{{ text|upper }}
{{ list|length }}
```

### Control Structures
```html
{% if condition %}
    <!-- ... -->
{% elif other_condition %}
    <!-- ... -->
{% else %}
    <!-- ... -->
{% endif %}

{% for item in items %}
    {{ item }}
{% endfor %}
```

### URL Generation
```html
{{ url_for('route_name') }}
{{ url_for('static', filename='css/main.css') }}
```

## Best Practices

1. **Extend base.html**: All pages should extend the base template
2. **Use blocks**: Override specific sections without duplicating code
3. **Escape output**: Jinja2 auto-escapes by default (safe from XSS)
4. **Keep logic minimal**: Complex logic belongs in views, not templates
5. **Use filters**: Format data in templates with built-in filters
6. **Organize includes**: Break large templates into smaller partials

## Template Organization

```
templates/
├── base.html              # Base layout
├── index.html             # Homepage
├── results.html           # Results page
├── error.html             # Error page
└── partials/              # Reusable components (optional)
    ├── _navigation.html
    ├── _footer.html
    └── _result_card.html
```

## Testing Templates

- Verify all links work
- Test with different data (empty, full, edge cases)
- Check responsive design
- Validate HTML (W3C validator)
- Test accessibility (screen readers, keyboard nav)
