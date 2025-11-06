# Images and Icons

Image assets for the CodeGuard web interface.

## Files

### `logo.png`
Main CodeGuard logo for branding.

**Specifications**:
- Format: PNG with transparency
- Dimensions: 400×100 pixels (4:1 ratio)
- Usage: Homepage header, documentation

### `logo-small.png`
Smaller logo variant for navigation.

**Specifications**:
- Format: PNG with transparency
- Dimensions: 120×30 pixels
- Usage: Navigation bar, compact displays

### `favicon.ico`
Browser favicon (multi-resolution).

**Specifications**:
- Format: ICO
- Sizes: 16×16, 32×32, 48×48
- Usage: Browser tabs, bookmarks

### `favicon.png`
PNG version of favicon.

**Specifications**:
- Format: PNG with transparency
- Dimensions: 192×192 pixels
- Usage: Modern browsers, PWA manifest

## Image Optimization

All images should be optimized for web:

```bash
# Optimize PNG files
optipng -o7 *.png

# Or use ImageOptim (Mac) / FileOptimizer (Windows)
```

## Usage in Templates

### Logo
```html
<img src="{{ url_for('static', filename='images/logo.png') }}"
     alt="CodeGuard Logo"
     width="400"
     height="100">
```

### Favicon
```html
<!-- In <head> section -->
<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='images/favicon.ico') }}">
<link rel="icon" type="image/png" href="{{ url_for('static', filename='images/favicon.png') }}">
```

## Creating Assets

### Logo Design Guidelines

- **Colors**: Use primary brand color (#2563eb)
- **Font**: Modern sans-serif (e.g., Inter, Poppins)
- **Style**: Clean, professional, academic
- **Elements**: Shield or guard icon optional
- **Text**: "CodeGuard" in title case

### Favicon Guidelines

- **Simple**: Works at 16×16 pixels
- **Recognizable**: Distinct shape/color
- **Contrast**: Visible on light and dark backgrounds
- **Monochrome**: Single color version for simplicity

## File Formats

| Format | Usage | Pros | Cons |
|--------|-------|------|------|
| PNG | Logos, icons | Transparency, lossless | Larger file size |
| JPG | Photos | Small file size | No transparency, lossy |
| SVG | Vector graphics | Scalable, small | Browser compatibility |
| ICO | Favicon | Multi-resolution | Legacy format |
| WebP | Modern images | Best compression | Limited old browser support |

## Responsive Images

For different screen densities:

```html
<img src="{{ url_for('static', filename='images/logo.png') }}"
     srcset="{{ url_for('static', filename='images/logo.png') }} 1x,
             {{ url_for('static', filename='images/logo@2x.png') }} 2x"
     alt="CodeGuard Logo">
```

## Alternative Text

Always provide descriptive alt text:

```html
<!-- Good -->
<img src="logo.png" alt="CodeGuard plagiarism detection logo">

<!-- Bad -->
<img src="logo.png" alt="logo">
```

## Lazy Loading

For images below the fold:

```html
<img src="image.png" alt="Description" loading="lazy">
```

## Icon Library (Optional)

Consider using icon libraries for UI icons:
- **Heroicons**: https://heroicons.com/
- **Feather Icons**: https://feathericons.com/
- **Font Awesome**: https://fontawesome.com/

## Image Specifications

### Logo Variants

| File | Size | Use Case |
|------|------|----------|
| logo.png | 400×100 | Desktop header |
| logo-small.png | 120×30 | Mobile header |
| logo@2x.png | 800×200 | Retina displays |
| logo-dark.png | 400×100 | Dark mode |

### Icons

| File | Size | Use Case |
|------|------|----------|
| favicon.ico | 16/32/48 | Browser favicon |
| favicon.png | 192×192 | PWA icon |
| apple-touch-icon.png | 180×180 | iOS home screen |

## Color Palette

For creating new assets:

```
Primary Blue:   #2563eb
Dark Blue:      #1e40af
Success Green:  #16a34a
Warning Orange: #f59e0b
Danger Red:     #dc2626
Gray:           #6b7280
```

## Version Control

- Include source files (e.g., .ai, .psd, .sketch) in separate directory
- Include only optimized versions in `static/images/`
- Document design decisions
- Maintain changelog for major updates

## Accessibility

- Sufficient contrast for logos
- SVG includes proper `<title>` and `<desc>` tags
- Decorative images use `alt=""`
- Informative images have descriptive alt text
