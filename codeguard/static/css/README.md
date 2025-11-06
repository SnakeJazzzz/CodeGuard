# CSS Stylesheets

Cascading stylesheets for the CodeGuard web interface.

## Files

### `main.css`
Global styles and layout framework.

**Includes**:
- CSS reset and normalization
- Typography (fonts, headings, paragraphs)
- Color scheme and CSS variables
- Layout grid and containers
- Navigation and header
- Footer
- Common components (buttons, forms, alerts)
- Responsive breakpoints

**Example Structure**:
```css
/* CSS Variables */
:root {
  --primary-color: #2563eb;
  --danger-color: #dc2626;
  --success-color: #16a34a;
  --warning-color: #f59e0b;

  --bg-color: #ffffff;
  --text-color: #1f2937;
  --border-color: #e5e7eb;

  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  --border-radius: 0.375rem;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--text-color);
  background: var(--bg-color);
  line-height: 1.6;
}

/* Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

/* Components */
.btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius);
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}
```

### `upload.css`
Styles specific to the file upload page.

**Includes**:
- Drag-and-drop dropzone
- File list display
- Upload progress bar
- File validation messages
- Upload button styles

**Key Components**:
```css
.upload-dropzone {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-xl);
  text-align: center;
  transition: all 0.3s ease;
}

.upload-dropzone--active {
  border-color: var(--primary-color);
  background: rgba(37, 99, 235, 0.05);
}

.file-list {
  margin-top: var(--spacing-lg);
}

.file-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-sm);
}

.file-item__name {
  font-family: monospace;
  color: var(--text-color);
}

.file-item__size {
  color: #6b7280;
  font-size: 0.875rem;
}
```

### `results.css`
Styles for the analysis results page.

**Includes**:
- Comparison matrix display
- Similarity score visualization
- Color-coded plagiarism indicators
- Score badges and labels
- Detail expansion panels

**Key Components**:
```css
.result-card {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.result-card--plagiarized {
  border-left: 4px solid var(--danger-color);
  background: rgba(220, 38, 38, 0.05);
}

.result-card--clean {
  border-left: 4px solid var(--success-color);
  background: rgba(22, 163, 74, 0.05);
}

.similarity-score {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}

.score-badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  font-weight: 600;
}

.score-badge--token {
  background: #dbeafe;
  color: #1e40af;
}

.score-badge--ast {
  background: #fef3c7;
  color: #92400e;
}

.score-badge--hash {
  background: #dcfce7;
  color: #166534;
}

.confidence-bar {
  width: 100%;
  height: 8px;
  background: var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.confidence-bar__fill {
  height: 100%;
  transition: width 0.3s ease;
}

.confidence-bar__fill--high {
  background: var(--danger-color);
}

.confidence-bar__fill--medium {
  background: var(--warning-color);
}

.confidence-bar__fill--low {
  background: var(--success-color);
}
```

## Design System

### Colors

```css
/* Primary */
--primary-color: #2563eb;      /* Blue */

/* Status */
--danger-color: #dc2626;       /* Red - Plagiarism */
--success-color: #16a34a;      /* Green - Clean */
--warning-color: #f59e0b;      /* Orange - Warning */
--info-color: #0891b2;         /* Cyan - Info */

/* Neutrals */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-500: #6b7280;
--gray-700: #374151;
--gray-900: #111827;
```

### Typography

```css
/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing

```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */
--spacing-2xl: 3rem;     /* 48px */
```

## Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 640px) {  /* sm */
  /* Tablet styles */
}

@media (min-width: 768px) {  /* md */
  /* Desktop styles */
}

@media (min-width: 1024px) { /* lg */
  /* Large desktop styles */
}
```

## Accessibility

- Sufficient color contrast (WCAG AA minimum)
- Focus indicators for keyboard navigation
- Readable font sizes (minimum 16px base)
- Clear hover/active states

## Browser Compatibility

All styles tested in:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Use CSS prefixes where needed:
```css
.element {
  -webkit-transform: scale(1.1);
  -ms-transform: scale(1.1);
  transform: scale(1.1);
}
```
