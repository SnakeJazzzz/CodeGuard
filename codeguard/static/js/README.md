# JavaScript Files

Client-side JavaScript for interactive functionality.

## Files

### `upload.js`
File upload handling and drag-and-drop functionality.

**Features**:
- Drag-and-drop file upload
- File validation (extension, size)
- File list preview
- Remove files before upload
- Progress indication
- AJAX form submission (optional)

**Example**:
```javascript
// upload.js

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const fileList = document.getElementById('fileList');

  // Drag and drop handlers
  dropzone.addEventListener('dragover', handleDragOver);
  dropzone.addEventListener('dragleave', handleDragLeave);
  dropzone.addEventListener('drop', handleDrop);

  // Click to select files
  dropzone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', handleFileSelect);
});

function handleDragOver(e) {
  e.preventDefault();
  e.currentTarget.classList.add('upload-dropzone--active');
}

function handleDragLeave(e) {
  e.currentTarget.classList.remove('upload-dropzone--active');
}

function handleDrop(e) {
  e.preventDefault();
  e.currentTarget.classList.remove('upload-dropzone--active');

  const files = Array.from(e.dataTransfer.files);
  validateAndDisplayFiles(files);
}

function handleFileSelect(e) {
  const files = Array.from(e.target.files);
  validateAndDisplayFiles(files);
}

function validateAndDisplayFiles(files) {
  // Filter .py files only
  const pyFiles = files.filter(f => f.name.endsWith('.py'));

  // Check file size
  const validFiles = pyFiles.filter(f => f.size <= 16 * 1024 * 1024);

  // Display file list
  displayFileList(validFiles);

  // Show warnings for invalid files
  if (pyFiles.length < files.length) {
    showWarning('Only .py files are accepted');
  }
  if (validFiles.length < pyFiles.length) {
    showWarning('Some files exceed 16MB limit');
  }
}

function displayFileList(files) {
  const listHTML = files.map(f => `
    <div class="file-item">
      <span class="file-item__name">${f.name}</span>
      <span class="file-item__size">${formatFileSize(f.size)}</span>
    </div>
  `).join('');

  fileList.innerHTML = listHTML;
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function showWarning(message) {
  // Display warning message
  console.warn(message);
}
```

### `results.js`
Results page interactivity and filtering.

**Features**:
- Sort results by confidence/similarity
- Filter by plagiarism status
- Expand/collapse detail panels
- Copy file names
- Highlight search terms

**Example**:
```javascript
// results.js

document.addEventListener('DOMContentLoaded', () => {
  const sortSelect = document.getElementById('sortBy');
  const filterSelect = document.getElementById('filterBy');

  sortSelect?.addEventListener('change', sortResults);
  filterSelect?.addEventListener('change', filterResults);

  // Initialize expand/collapse
  initializeDetailPanels();
});

function sortResults() {
  const sortBy = document.getElementById('sortBy').value;
  const results = Array.from(document.querySelectorAll('.result-card'));

  results.sort((a, b) => {
    const aValue = parseFloat(a.dataset[sortBy]);
    const bValue = parseFloat(b.dataset[sortBy]);
    return bValue - aValue; // Descending
  });

  const container = document.getElementById('resultsContainer');
  results.forEach(card => container.appendChild(card));
}

function filterResults() {
  const filter = document.getElementById('filterBy').value;
  const results = document.querySelectorAll('.result-card');

  results.forEach(card => {
    const isPlagiarized = card.classList.contains('result-card--plagiarized');

    if (filter === 'all') {
      card.style.display = 'block';
    } else if (filter === 'plagiarized' && isPlagiarized) {
      card.style.display = 'block';
    } else if (filter === 'clean' && !isPlagiarized) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

function initializeDetailPanels() {
  const toggleButtons = document.querySelectorAll('.detail-toggle');

  toggleButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      const panel = this.nextElementSibling;
      panel.classList.toggle('detail-panel--open');
      this.textContent = panel.classList.contains('detail-panel--open')
        ? 'Hide Details'
        : 'Show Details';
    });
  });
}
```

### `progress.js`
Progress indicators and loading states.

**Features**:
- Upload progress bar
- Analysis progress spinner
- Estimated time remaining
- Success/error notifications

**Example**:
```javascript
// progress.js

class ProgressIndicator {
  constructor(elementId) {
    this.element = document.getElementById(elementId);
    this.progressBar = this.element.querySelector('.progress-bar__fill');
    this.percentText = this.element.querySelector('.progress-percent');
  }

  show() {
    this.element.style.display = 'block';
  }

  hide() {
    this.element.style.display = 'none';
  }

  setProgress(percent) {
    this.progressBar.style.width = percent + '%';
    this.percentText.textContent = Math.round(percent) + '%';
  }

  showSpinner() {
    this.element.innerHTML = `
      <div class="spinner"></div>
      <p>Analyzing files...</p>
    `;
    this.show();
  }

  showSuccess(message) {
    this.element.innerHTML = `
      <div class="success-icon">✓</div>
      <p>${message}</p>
    `;
    setTimeout(() => this.hide(), 3000);
  }

  showError(message) {
    this.element.innerHTML = `
      <div class="error-icon">✗</div>
      <p>${message}</p>
    `;
  }
}

// Usage
const progress = new ProgressIndicator('progressIndicator');

function uploadFiles(files) {
  progress.showSpinner();

  // Simulate upload progress
  let percent = 0;
  const interval = setInterval(() => {
    percent += 10;
    progress.setProgress(percent);

    if (percent >= 100) {
      clearInterval(interval);
      progress.showSuccess('Upload complete!');
    }
  }, 500);
}
```

### `utils.js`
Shared utility functions.

**Functions**:
```javascript
// utils.js

// Format file size
function formatFileSize(bytes) {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return size.toFixed(1) + ' ' + units[unitIndex];
}

// Format percentage
function formatPercent(value) {
  return (value * 100).toFixed(1) + '%';
}

// Debounce function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Show toast notification
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.textContent = message;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast--visible');
  }, 100);

  setTimeout(() => {
    toast.classList.remove('toast--visible');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Copy to clipboard
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast('Copied to clipboard', 'success');
  } catch (err) {
    showToast('Failed to copy', 'error');
  }
}

// Export functions
window.CodeGuardUtils = {
  formatFileSize,
  formatPercent,
  debounce,
  showToast,
  copyToClipboard
};
```

## Best Practices

### Progressive Enhancement
- Core functionality works without JavaScript
- JavaScript enhances user experience
- Graceful degradation for older browsers

### Error Handling
```javascript
try {
  // Risky operation
} catch (error) {
  console.error('Operation failed:', error);
  showToast('An error occurred', 'error');
}
```

### Performance
- Debounce expensive operations
- Use event delegation for dynamic content
- Minimize DOM manipulation
- Cache DOM queries

### Accessibility
- Keyboard navigation support
- ARIA attributes for dynamic content
- Focus management
- Screen reader friendly

## Testing

Manual testing checklist:
- [ ] Drag and drop works
- [ ] File validation works
- [ ] Progress indicators display
- [ ] Results sorting works
- [ ] Results filtering works
- [ ] Mobile responsive
- [ ] Keyboard accessible
- [ ] Works without JavaScript (core features)
