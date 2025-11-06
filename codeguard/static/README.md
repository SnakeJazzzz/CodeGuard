# Static Assets

Static web assets including CSS stylesheets, JavaScript files, and images.

## Structure

```
static/
├── css/         # Stylesheets
├── js/          # JavaScript files
└── images/      # Images and icons
```

## Asset Organization

### CSS Files (`css/`)
- `main.css` - Global styles and layout
- `upload.css` - Upload page specific styles
- `results.css` - Results page specific styles

### JavaScript Files (`js/`)
- `upload.js` - File upload handling and drag-and-drop
- `results.js` - Results page interactivity
- `progress.js` - Progress bar and loading indicators
- `utils.js` - Shared utility functions

### Images (`images/`)
- `logo.png` - CodeGuard logo
- `favicon.ico` - Browser favicon
- Icons and illustrations

## Usage in Templates

Reference static files in Jinja2 templates:

```html
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">

<!-- JavaScript -->
<script src="{{ url_for('static', filename='js/upload.js') }}"></script>

<!-- Images -->
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="CodeGuard">
```

## Development

### CSS

Follow these conventions:
- Use BEM naming methodology
- Mobile-first responsive design
- CSS variables for colors and spacing
- Minimize use of !important

Example:
```css
:root {
  --primary-color: #2563eb;
  --danger-color: #dc2626;
  --success-color: #16a34a;
}

.upload-form {
  /* Styles */
}

.upload-form__dropzone {
  /* Styles */
}
```

### JavaScript

Follow these conventions:
- ES6+ syntax
- Progressive enhancement
- No framework dependencies
- Clear function names
- Comments for complex logic

Example:
```javascript
// File upload handling
document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');

  dropzone.addEventListener('drop', handleFileDrop);
});

function handleFileDrop(event) {
  event.preventDefault();
  // Handle file drop
}
```

## Browser Support

Target modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

Optimization techniques:
- Minify CSS and JS for production
- Compress images
- Use WebP format for images
- Lazy load non-critical assets
- Cache static files

## Asset Pipeline

### Development
- Serve unminified files
- Include source maps
- Hot reload (if using Flask debug mode)

### Production
- Minify and concatenate
- Add cache-busting hashes
- Compress with gzip
- Set far-future expires headers

## File Organization

```
static/
├── css/
│   ├── main.css           # Global styles (layout, typography)
│   ├── upload.css         # Upload page (drag-drop, file list)
│   ├── results.css        # Results page (comparison matrix, scores)
│   └── components.css     # Reusable components (optional)
├── js/
│   ├── upload.js          # Upload functionality
│   ├── results.js         # Results interactivity
│   ├── progress.js        # Progress indicators
│   └── utils.js           # Utility functions
└── images/
    ├── logo.png           # Main logo
    ├── logo-small.png     # Small logo for header
    ├── favicon.ico        # Browser favicon
    └── favicon.png        # PNG favicon
```

## Testing

Test static assets:
- Validate CSS (W3C CSS Validator)
- Lint JavaScript (ESLint)
- Test in all target browsers
- Check responsive design
- Verify accessibility

## Version Control

Include in repository:
- All source files
- Development versions
- Exclude minified versions (generate during build)
- Exclude node_modules (if using build tools)
