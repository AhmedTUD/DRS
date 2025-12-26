// Main JavaScript file for Daily Report System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Add fade-in animation to cards
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        setTimeout(function() {
            card.classList.add('fade-in');
        }, index * 100);
    });

    // Form validation enhancement
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                var firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            form.classList.add('was-validated');
        });
    });

    // Enhanced table interactions
    var tables = document.querySelectorAll('.table tbody tr');
    tables.forEach(function(row) {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Smooth scrolling for anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Loading state for buttons (exclude report forms which handle their own submission)
    var submitButtons = document.querySelectorAll('button[type="submit"]:not(#reportForm button)');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var form = this.closest('form');
            if (form && form.checkValidity() && !form.id.includes('reportForm')) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Submitting...';
                this.disabled = true;
            }
        });
    });
});

// Utility functions
function showAlert(message, type = 'info') {
    // Map error type to danger for Bootstrap
    if (type === 'error') type = 'danger';
    
    var alertContainer = document.querySelector('.container-fluid');
    if (!alertContainer) {
        alertContainer = document.querySelector('main') || document.body;
    }
    
    var alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.style.position = 'relative';
    alert.style.zIndex = '1050';
    alert.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at the top of the container
    if (alertContainer.firstChild) {
        alertContainer.insertBefore(alert, alertContainer.firstChild);
    } else {
        alertContainer.appendChild(alert);
    }
    
    // Scroll to alert if not visible
    alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Auto-hide after 5 seconds
    setTimeout(function() {
        if (alert && alert.parentNode) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

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

// Export function for reports
function exportToExcel(data, filename) {
    var csv = convertToCSV(data);
    var blob = new Blob([csv], { type: 'text/csv' });
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    var headers = Object.keys(data[0]);
    var csv = headers.join(',') + '\n';
    
    data.forEach(function(row) {
        var values = headers.map(function(header) {
            var value = row[header] || '';
            // Escape commas and quotes
            if (value.toString().includes(',') || value.toString().includes('"')) {
                value = '"' + value.toString().replace(/"/g, '""') + '"';
            }
            return value;
        });
        csv += values.join(',') + '\n';
    });
    
    return csv;
}

// Mobile-friendly interactions
if ('ontouchstart' in window) {
    // Add touch-friendly classes
    document.body.classList.add('touch-device');
    
    // Increase button sizes on mobile
    var buttons = document.querySelectorAll('.btn');
    buttons.forEach(function(button) {
        button.style.minHeight = '44px';
        button.style.minWidth = '44px';
    });
}

// Network status handling
window.addEventListener('online', function() {
    showAlert('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showAlert('Connection lost. Please check your internet connection.', 'warning');
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + S to save forms
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        var submitButton = document.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.click();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        var modals = document.querySelectorAll('.modal.show');
        modals.forEach(function(modal) {
            var bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            var loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log('Page load time:', loadTime + 'ms');
        }, 0);
    });
}

// Enhanced form handling for dynamic user management
document.addEventListener('DOMContentLoaded', function() {
    // Auto-generate store codes based on store names
    document.addEventListener('input', function(e) {
        if (e.target.name === 'new_store_names[]') {
            const row = e.target.closest('.new-store-row');
            const codeInput = row.querySelector('input[name="new_store_codes[]"]');
            
            if (codeInput && !codeInput.value) {
                // Generate code from name (first 3 letters + random number)
                const name = e.target.value.trim();
                if (name.length >= 3) {
                    const code = name.substring(0, 3).toUpperCase() + '-' + 
                                Math.floor(Math.random() * 1000).toString().padStart(3, '0');
                    codeInput.value = code;
                }
            }
        }
    });

    // Real-time validation for store codes
    document.addEventListener('blur', function(e) {
        if (e.target.name === 'new_store_codes[]') {
            validateStoreCode(e.target);
        }
    });

    // Enhanced area selection handling
    document.addEventListener('change', function(e) {
        if (e.target.name === 'assigned_areas') {
            updateStoreAreaOptions();
        }
    });
});

function validateStoreCode(input) {
    const code = input.value.trim();
    if (code) {
        // Check for duplicate codes in the same form
        const allCodes = document.querySelectorAll('input[name="new_store_codes[]"]');
        let duplicateFound = false;
        
        allCodes.forEach(codeInput => {
            if (codeInput !== input && codeInput.value.trim() === code) {
                duplicateFound = true;
            }
        });
        
        if (duplicateFound) {
            input.classList.add('is-invalid');
            showTooltip(input, 'Store code already exists in this form');
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            hideTooltip(input);
        }
    }
}

function updateStoreAreaOptions() {
    // Update area dropdowns in new store rows based on selected areas
    const selectedAreas = document.querySelectorAll('input[name="assigned_areas"]:checked');
    const storeAreaSelects = document.querySelectorAll('select[name="new_store_areas[]"]');
    
    storeAreaSelects.forEach(select => {
        // Keep existing options but highlight selected areas
        const options = select.querySelectorAll('option');
        options.forEach(option => {
            if (option.value) {
                const isSelected = Array.from(selectedAreas).some(area => area.value === option.value);
                if (isSelected) {
                    option.style.fontWeight = 'bold';
                    option.style.color = '#198754';
                } else {
                    option.style.fontWeight = 'normal';
                    option.style.color = '';
                }
            }
        });
    });
}

function showTooltip(element, message) {
    // Remove existing tooltip
    hideTooltip(element);
    
    const tooltip = document.createElement('div');
    tooltip.className = 'invalid-tooltip';
    tooltip.textContent = message;
    tooltip.style.position = 'absolute';
    tooltip.style.top = '100%';
    tooltip.style.left = '0';
    tooltip.style.zIndex = '1000';
    tooltip.style.backgroundColor = '#dc3545';
    tooltip.style.color = 'white';
    tooltip.style.padding = '4px 8px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.fontSize = '12px';
    tooltip.style.marginTop = '2px';
    
    element.parentNode.style.position = 'relative';
    element.parentNode.appendChild(tooltip);
}

function hideTooltip(element) {
    const tooltip = element.parentNode.querySelector('.invalid-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Enhanced store management functions
function addNewStoreWithValidation() {
    // Check if previous rows are filled
    const existingRows = document.querySelectorAll('.new-store-row');
    for (let row of existingRows) {
        const inputs = row.querySelectorAll('input[required], select[required]');
        for (let input of inputs) {
            if (!input.value.trim()) {
                input.focus();
                showAlert('Please fill in all fields in existing store rows before adding a new one', 'warning');
                return;
            }
        }
    }
    
    addNewStore();
}

// Bulk operations for areas and stores
function selectAllAreas() {
    const checkboxes = document.querySelectorAll('input[name="assigned_areas"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    updateStoreAreaOptions();
}

function deselectAllAreas() {
    const checkboxes = document.querySelectorAll('input[name="assigned_areas"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    updateStoreAreaOptions();
}

function selectAllStores() {
    const checkboxes = document.querySelectorAll('input[name="assigned_stores"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
}

function deselectAllStores() {
    const checkboxes = document.querySelectorAll('input[name="assigned_stores"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
}

// Form submission with loading state
function submitFormWithLoading(formId) {
    const form = document.getElementById(formId);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Re-enable after 10 seconds as fallback
        setTimeout(() => {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }, 10000);
    }
}

// Auto-save draft functionality (optional)
function saveDraft(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const draftData = {};
    
    for (let [key, value] of formData.entries()) {
        if (draftData[key]) {
            if (Array.isArray(draftData[key])) {
                draftData[key].push(value);
            } else {
                draftData[key] = [draftData[key], value];
            }
        } else {
            draftData[key] = value;
        }
    }
    
    localStorage.setItem(`draft_${formId}`, JSON.stringify(draftData));
    showAlert('Draft saved', 'info');
}

function loadDraft(formId) {
    const draftData = localStorage.getItem(`draft_${formId}`);
    if (draftData) {
        try {
            const data = JSON.parse(draftData);
            const form = document.getElementById(formId);
            
            Object.keys(data).forEach(key => {
                const elements = form.querySelectorAll(`[name="${key}"]`);
                elements.forEach(element => {
                    if (element.type === 'checkbox' || element.type === 'radio') {
                        element.checked = Array.isArray(data[key]) ? 
                            data[key].includes(element.value) : 
                            data[key] === element.value;
                    } else {
                        element.value = Array.isArray(data[key]) ? data[key][0] : data[key];
                    }
                });
            });
            
            showAlert('Draft loaded', 'success');
        } catch (e) {
            console.error('Error loading draft:', e);
        }
    }
}

function clearDraft(formId) {
    localStorage.removeItem(`draft_${formId}`);
    showAlert('Draft cleared', 'info');
}

// Enhanced form handling for user management
function submitFormWithLoading(formId) {
    const form = document.getElementById(formId);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
        
        // Re-enable after 15 seconds as fallback
        setTimeout(() => {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }, 15000);
    }
}

// Enhanced area and store management functions
window.areaStoreManager = {
    // Validate area name
    validateAreaName: function(name) {
        if (!name || name.trim().length < 2) {
            return { valid: false, message: 'Area name must be at least 2 characters long' };
        }
        
        if (name.length > 50) {
            return { valid: false, message: 'Area name must be less than 50 characters' };
        }
        
        if (!/^[a-zA-Z0-9\s\-_]+$/.test(name)) {
            return { valid: false, message: 'Area name can only contain letters, numbers, spaces, hyphens, and underscores' };
        }
        
        return { valid: true };
    },
    
    // Validate store data
    validateStore: function(name, code) {
        const errors = [];
        
        if (!name || name.trim().length < 2) {
            errors.push('Store name must be at least 2 characters long');
        }
        
        if (!code || code.trim().length < 3) {
            errors.push('Store code must be at least 3 characters long');
        }
        
        if (code && !/^[A-Z0-9\-_]+$/.test(code)) {
            errors.push('Store code can only contain uppercase letters, numbers, hyphens, and underscores');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    },
    
    // Generate unique store code
    generateStoreCode: function(storeName, existingCodes = []) {
        if (!storeName) return '';
        
        // Clean the name and take first 3 characters
        const cleanName = storeName.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
        const prefix = cleanName.substring(0, 3).padEnd(3, 'X');
        
        // Generate unique suffix
        let suffix = 1;
        let code = `${prefix}-${suffix.toString().padStart(3, '0')}`;
        
        while (existingCodes.includes(code)) {
            suffix++;
            code = `${prefix}-${suffix.toString().padStart(3, '0')}`;
        }
        
        return code;
    },
    
    // Get all existing store codes
    getExistingStoreCodes: function() {
        const codes = [];
        
        // Get codes from existing stores (checkboxes)
        document.querySelectorAll('input[name="assigned_stores"]').forEach(checkbox => {
            const label = document.querySelector(`label[for="${checkbox.id}"]`);
            if (label) {
                const match = label.textContent.match(/- ([A-Z0-9\-_]+)/);
                if (match) codes.push(match[1]);
            }
        });
        
        // Get codes from new store inputs
        document.querySelectorAll('input[name="new_store_codes[]"]').forEach(input => {
            if (input.value.trim()) codes.push(input.value.trim());
        });
        
        return codes;
    }
};

// Enhanced keyboard navigation
document.addEventListener('keydown', function(e) {
    // Tab navigation enhancement for dynamic forms
    if (e.key === 'Tab') {
        const activeElement = document.activeElement;
        
        // If in a new store row, handle tab navigation
        if (activeElement && activeElement.closest('.new-store-row')) {
            const row = activeElement.closest('.new-store-row');
            const inputs = row.querySelectorAll('input, select, button');
            const currentIndex = Array.from(inputs).indexOf(activeElement);
            
            if (e.shiftKey && currentIndex === 0) {
                // Shift+Tab from first input - go to previous row or add area button
                e.preventDefault();
                const prevRow = row.previousElementSibling;
                if (prevRow && prevRow.classList.contains('new-store-row')) {
                    const prevInputs = prevRow.querySelectorAll('input, select, button');
                    prevInputs[prevInputs.length - 1].focus();
                } else {
                    document.getElementById('new_area_name').focus();
                }
            } else if (!e.shiftKey && currentIndex === inputs.length - 1) {
                // Tab from last input - go to next row or create new row
                e.preventDefault();
                const nextRow = row.nextElementSibling;
                if (nextRow && nextRow.classList.contains('new-store-row')) {
                    nextRow.querySelector('input').focus();
                } else {
                    // Create new row and focus first input
                    if (typeof addNewStore === 'function') {
                        addNewStore();
                        setTimeout(() => {
                            const newRow = document.querySelector('.new-store-row:last-child');
                            if (newRow) {
                                newRow.querySelector('input').focus();
                            }
                        }, 100);
                    }
                }
            }
        }
    }
});

// Auto-save functionality for forms
let autoSaveTimer;
function enableAutoSave(formId, interval = 30000) { // 30 seconds
    const form = document.getElementById(formId);
    if (!form) return;
    
    function saveFormData() {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        localStorage.setItem(`autosave_${formId}`, JSON.stringify({
            data: data,
            timestamp: Date.now()
        }));
    }
    
    // Save on form changes
    form.addEventListener('input', function() {
        clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(saveFormData, 2000); // Save 2 seconds after last change
    });
    
    // Periodic save
    setInterval(saveFormData, interval);
}

// Load auto-saved data
function loadAutoSavedData(formId) {
    const saved = localStorage.getItem(`autosave_${formId}`);
    if (!saved) return false;
    
    try {
        const { data, timestamp } = JSON.parse(saved);
        const age = Date.now() - timestamp;
        
        // Only load if less than 1 hour old
        if (age > 3600000) {
            localStorage.removeItem(`autosave_${formId}`);
            return false;
        }
        
        const form = document.getElementById(formId);
        if (!form) return false;
        
        // Show confirmation
        if (confirm('Auto-saved data found. Would you like to restore it?')) {
            Object.keys(data).forEach(key => {
                const elements = form.querySelectorAll(`[name="${key}"]`);
                elements.forEach(element => {
                    if (element.type === 'checkbox' || element.type === 'radio') {
                        element.checked = Array.isArray(data[key]) ? 
                            data[key].includes(element.value) : 
                            data[key] === element.value;
                    } else {
                        element.value = Array.isArray(data[key]) ? data[key][0] : data[key];
                    }
                });
            });
            
            showAlert('Auto-saved data restored successfully', 'success');
            return true;
        }
    } catch (e) {
        console.error('Error loading auto-saved data:', e);
        localStorage.removeItem(`autosave_${formId}`);
    }
    
    return false;
}

// Clear auto-saved data on successful form submission
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.id) {
        localStorage.removeItem(`autosave_${form.id}`);
    }
});

// Initialize auto-save for user forms
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('createUserForm')) {
        enableAutoSave('createUserForm');
        loadAutoSavedData('createUserForm');
    }
    
    if (document.getElementById('editUserForm')) {
        enableAutoSave('editUserForm');
        loadAutoSavedData('editUserForm');
    }
});