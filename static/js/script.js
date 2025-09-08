/**
 * DMP ART - Complete JavaScript Functionality
 * Enhanced with proper error handling, debugging, and responsive design
 */

// ===========================================
// MAIN INITIALIZATION
// ===========================================

document.addEventListener('DOMContentLoaded', function () {
    try {
        // Initialize core functionality
        initializeDarkMode();
        initializeUploadPage();
        initializeReviewPage();
        initializeTemplateEditor();
    } catch (error) {
        console.error('DMP ART: Error during initialization:', error);
    }
});

// ===========================================
// DARK MODE FUNCTIONALITY
// ===========================================

function initializeDarkMode() {
    try {
        // Load saved theme preference or detect system preference
        const savedTheme = localStorage.getItem('dmp-art-theme');
        const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');

        // Set initial theme
        setTheme(initialTheme);
        updateToggleButton(initialTheme);

        // Add keyboard shortcut
        addDarkModeKeyboardShortcut();

        // Listen for system theme changes
        listenForSystemThemeChanges();
    } catch (error) {
        console.error('Error initializing dark mode:', error);
    }
}

function toggleTheme() {
    try {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        setTheme(newTheme);
        updateToggleButton(newTheme);
        localStorage.setItem('dmp-art-theme', newTheme);
    } catch (error) {
        console.error('Error toggling theme:', error);
    }
}

function setTheme(theme) {
    try {
        document.documentElement.setAttribute('data-theme', theme);

        // Update meta theme color
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ?
                '#121212' : '#ffffff');
        }
    } catch (error) {
        console.error('Error setting theme:', error);
    }
}

function updateToggleButton(theme) {
    try {
        const themeText = document.getElementById('theme-text');
        const themeIcon = document.querySelector('.theme-toggle i');

        if (themeText) {
            if (theme === 'dark') {
                themeText.textContent = 'Light Mode';
            } else {
                themeText.textContent = 'Dark Mode';
            }
        }

        if (themeIcon) {
            // Sun for dark mode (to switch to light), moon for light mode (to switch to dark)
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    } catch (error) {
        console.error('Error updating toggle button:', error);
    }
}

function addDarkModeKeyboardShortcut() {
    try {
        document.addEventListener('keydown', function (e) {
            // Ctrl/Cmd + Shift + D to toggle dark mode
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                toggleTheme();
            }
        });
    } catch (error) {
        console.error('Error adding keyboard shortcut:', error);
    }
}

function listenForSystemThemeChanges() {
    try {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

            mediaQuery.addEventListener('change', function (e) {
                // Only auto-switch if user hasn't manually set a preference
                if (!localStorage.getItem('dmp-art-theme')) {
                    const newTheme = e.matches ? 'dark' : 'light';
                    setTheme(newTheme);
                    updateToggleButton(newTheme);
                }
            });
        }
    } catch (error) {
        console.error('Error setting up system theme listener:', error);
    }
}

// ===========================================
// UPLOAD PAGE FUNCTIONALITY
// ===========================================

function initializeUploadPage() {

    // Get all required elements
    const elements = {
        dropArea: document.getElementById('drop-area'),
        fileInput: document.getElementById('file-input'),
        fileInfo: document.getElementById('file-info'),
        fileName: document.getElementById('file-name'),
        uploadBtn: document.getElementById('upload-btn'),
        clearBtn: document.getElementById('clear-btn'),
        loading: document.getElementById('loading'),
        result: document.getElementById('result'),
        successMessage: document.getElementById('success-message'),
        errorMessage: document.getElementById('error-message'),
        errorText: document.getElementById('error-text'),
        downloadBtn: document.getElementById('download-btn')
    };

    // Exit if not on upload page
    if (!elements.dropArea && !elements.fileInput) {
        return;
    }

    try {
        setupDragAndDrop(elements);
        setupFileSelection(elements);
        setupUploadButton(elements);
        setupClearButton(elements);

    } catch (error) {
        console.error('Error initializing upload page:', error);
    }
}

function setupDragAndDrop(elements) {
    const { dropArea } = elements;
    if (!dropArea) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    dropArea.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropArea.classList.add('drag-over');
    }

    function unhighlight() {
        dropArea.classList.remove('drag-over');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            handleFileSelection(files[0], elements);
        }
    }
}

function setupFileSelection(elements) {
    const { fileInput, dropArea } = elements;

    // Make the entire upload area clickable
    if (dropArea) {
        dropArea.addEventListener('click', () => {
            if (fileInput) fileInput.click();
        });
        // Add cursor pointer style to indicate clickability
        dropArea.style.cursor = 'pointer';
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0], elements);
            }
        });
    }
}

function handleFileSelection(file, elements) {
    const { fileInfo, fileName, uploadBtn } = elements;


    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const allowedExtensions = ['.pdf', '.docx'];

    const isValidType = allowedTypes.includes(file.type) ||
        allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

    if (!isValidType) {
        showToast('Please select a PDF or DOCX file', 'error');
        return;
    }

    // Validate file size (16MB limit)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('File size must be less than 16MB', 'error');
        return;
    }

    // Store file and update UI
    elements.selectedFile = file;
    updateButtonStates(elements, 'file-selected');

    if (fileName) {
        fileName.textContent = file.name;
    }

    if (fileInfo) {
        fileInfo.style.display = 'block';
    }

    if (uploadBtn) {
        uploadBtn.disabled = false;
        uploadBtn.style.opacity = '1';
    }

    showToast('File selected successfully');
}

function setupUploadButton(elements) {
    const { uploadBtn } = elements;

    if (uploadBtn) {
        uploadBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering the drop area click
            if (elements.selectedFile && !uploadBtn.disabled) {
                updateButtonStates(elements, 'analyzing');
                uploadFile(elements.selectedFile, elements);
            } else if (!elements.selectedFile) {
                showToast('Please select a file first', 'error');
            }
        });
    }

    // Initialize button states
    updateButtonStates(elements, 'initial');
}

function setupClearButton(elements) {
    const { clearBtn, fileInput, fileInfo, fileName, uploadBtn } = elements;

    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering the drop area click
            elements.selectedFile = null;
            updateButtonStates(elements, 'initial');

            if (fileInput) fileInput.value = '';
            if (fileInfo) fileInfo.style.display = 'none';
            if (fileName) fileName.textContent = '';

            showToast('File cleared');
        });
    }
}

// Button state management
function updateButtonStates(elements, state) {
    const { uploadBtn, clearBtn } = elements;
    
    // Remove all state classes
    [uploadBtn, clearBtn].forEach(btn => {
        if (btn) {
            btn.disabled = false;
            btn.classList.remove('btn-active');
        }
    });
    
    switch (state) {
        case 'initial':
            // Upload disabled, clear disabled
            if (uploadBtn) uploadBtn.disabled = true;
            if (clearBtn) clearBtn.disabled = true;
            break;
            
        case 'file-selected':
            // Upload and clear active
            if (uploadBtn) uploadBtn.classList.add('btn-active');
            if (clearBtn) clearBtn.classList.add('btn-active');
            break;
            
        case 'analyzing':
            // Only clear active
            if (uploadBtn) uploadBtn.disabled = true;
            if (clearBtn) clearBtn.classList.add('btn-active');
            break;
    }
}

function uploadFile(file, elements) {
    const { loading, result, successMessage, errorMessage, errorText } = elements;


    const formData = new FormData();
    formData.append('file', file);

    // Show loading state
    if (loading) {
        loading.style.display = 'block';
    }

    // Hide previous results
    if (result) result.style.display = 'none';
    if (successMessage) successMessage.style.display = 'none';
    if (errorMessage) errorMessage.style.display = 'none';

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {

            // Hide loading
            if (loading) {
                loading.style.display = 'none';
            }

            if (data.success && data.redirect) {
                // Center the success message
                if (successMessage) {
                    successMessage.style.position = 'fixed';
                    successMessage.style.top = '50%';
                    successMessage.style.left = '50%';
                    successMessage.style.transform = 'translate(-50%, -50%)';
                    successMessage.style.zIndex = '1000';
                    successMessage.style.maxWidth = '90%';
                    successMessage.style.width = 'auto';
                    successMessage.style.display = 'block';
                }

                showToast('File processed successfully!');

                // Redirect after showing success message
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 2000);
            } else {
                // Show error
                if (errorMessage) {
                    errorMessage.style.display = 'block';
                }
                if (errorText) {
                    errorText.textContent = data.message || 'Unknown error occurred';
                }

                showToast(data.message || 'Upload failed', 'error');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);

            // Hide loading
            if (loading) {
                loading.style.display = 'none';
            }

            // Show error
            if (errorMessage) {
                errorMessage.style.display = 'block';
            }
            if (errorText) {
                errorText.textContent = 'Network error occurred';
            }

            showToast('Network error occurred', 'error');
        });
}

// ===========================================
// REVIEW PAGE FUNCTIONALITY
// ===========================================

function initializeReviewPage() {

    const elements = {
        commentButtons: document.querySelectorAll('.comment-btn'),
        compileButton: document.getElementById('compile-feedback-btn'),
        copyButtons: document.querySelectorAll('.copy-btn'),
        resetButtons: document.querySelectorAll('.reset-btn'),
        clearButtons: document.querySelectorAll('.clear-btn'),
        compiledContainer: document.getElementById('compiled-feedback-container'),
        compiledTextarea: document.getElementById('compiled-feedback'),
        closeCompiledButton: document.getElementById('close-compiled-btn'),
        saveFeedbackButton: document.getElementById('save-feedback-btn')
    };

    // Exit if not on review page
    if (!elements.commentButtons.length && !elements.compileButton) {
        return;
    }

    try {
        initializeSectionNavigation();
        setupCommentButtons(elements);
        setupFeedbackButtons(elements);
        setupCompileButton(elements);
        setupSaveFeedbackButton(elements);
        initializeCharacterCounters();

    } catch (error) {
        console.error('Error initializing review page:', error);
    }
}

function setupCommentButtons(elements) {
    const { commentButtons } = elements;

    commentButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const comment = this.getAttribute('data-comment');

            if (id && comment) {
                insertCommentWithAnimation(id, comment);
            }
        });
    });
}

function setupFeedbackButtons(elements) {
    const { copyButtons, resetButtons, clearButtons } = elements;

    // Copy buttons
    copyButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const textarea = document.getElementById(`feedback-${id}`);

            if (textarea) {
                copyToClipboard(textarea.value)
                    .then(() => showToast('Feedback copied to clipboard!'))
                    .catch(() => showToast('Failed to copy feedback', 'error'));
            }
        });
    });

    // Reset buttons
    resetButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const textarea = document.getElementById(`feedback-${id}`);

            if (textarea && window.originalTemplates && window.originalTemplates[id]) {
                textarea.value = window.originalTemplates[id];
                updateCharacterCounter(id);
                showToast('Feedback reset to original template');
            }
        });
    });

    // Clear buttons
    clearButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const textarea = document.getElementById(`feedback-${id}`);

            if (textarea) {
                textarea.value = '';
                updateCharacterCounter(id);
                showToast('Feedback cleared');
            }
        });
    });
}

function setupCompileButton(elements) {
    const { compileButton, compiledContainer, compiledTextarea, closeCompiledButton } = elements;

    if (compileButton) {
        compileButton.addEventListener('click', function () {
            const compiledFeedback = compileFeedback();

            if (compiledTextarea) {
                compiledTextarea.value = compiledFeedback;
            }

            if (compiledContainer) {
                compiledContainer.classList.remove('hidden');
            }
        });
    }

    if (closeCompiledButton && compiledContainer) {
        closeCompiledButton.addEventListener('click', function () {
            compiledContainer.classList.add('hidden');
        });
    }
}

function setupSaveFeedbackButton(elements) {
    const { saveFeedbackButton } = elements;

    if (saveFeedbackButton) {
        saveFeedbackButton.addEventListener('click', function () {
            saveFeedback();
        });
    }
}

function insertCommentWithAnimation(id, comment) {
    const textarea = document.getElementById(`feedback-${id}`);
    if (!textarea) return;

    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;
    const currentValue = textarea.value;

    // Determine prefix for proper formatting
    let prefix = '';
    if (startPos > 0 && currentValue.charAt(startPos - 1) !== '\n') {
        prefix = '\n';
    }

    // Insert comment
    const newValue = currentValue.substring(0, startPos) + prefix + comment + currentValue.substring(endPos);
    textarea.value = newValue;

    // Set cursor position after inserted comment
    const newCursorPos = startPos + prefix.length + comment.length;
    textarea.setSelectionRange(newCursorPos, newCursorPos);

    // Focus textarea
    textarea.focus();

    // Update character counter
    updateCharacterCounter(id);

    // Visual feedback
    textarea.style.backgroundColor = 'var(--bg-hover)';
    setTimeout(() => {
        textarea.style.backgroundColor = '';
    }, 300);

}

function compileFeedback() {
    const feedbackElements = document.querySelectorAll('.feedback-text');
    const sections = [];

    feedbackElements.forEach(textarea => {
        const sectionId = textarea.id.replace('feedback-', '');
        const sectionTitle = getSectionTitle(sectionId);
        const feedbackText = textarea.value.trim();

        if (feedbackText) {
            sections.push({
                id: sectionId,
                title: sectionTitle,
                feedback: feedbackText
            });
        }
    });

    // Generate compiled feedback
    let compiled = `DMP Feedback Report\n`;
    compiled += `Generated: ${new Date().toLocaleString()}\n`;
    compiled += `Total sections with feedback: ${sections.length}\n\n`;
    compiled += '=' * 50 + '\n\n';

    sections.forEach((section, index) => {
        compiled += `${index + 1}. ${section.title}\n`;
        compiled += '-'.repeat(section.title.length + 3) + '\n';
        compiled += `${section.feedback}\n\n`;
    });

    return compiled;
}

function saveFeedback() {
    const feedbackData = {};

    document.querySelectorAll('.feedback-text').forEach(textarea => {
        const sectionId = textarea.id.replace('feedback-', '');
        feedbackData[sectionId] = textarea.value;
    });

    fetch('/save_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedbackData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Feedback saved successfully!');
            } else {
                showToast('Error saving feedback: ' + (data.message || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error saving feedback:', error);
            showToast('Error saving feedback', 'error');
        });
}

// ===========================================
// SECTION NAVIGATION
// ===========================================

function initializeSectionNavigation() {

    try {
        createSectionNavigation();
    } catch (error) {
        console.error('Error initializing section navigation:', error);
    }
}

function createSectionNavigation() {
    // Skip navigation creation on review page - handled by review.html
    if (document.body.hasAttribute('data-page') && document.body.getAttribute('data-page') === 'review') {
        return;
    }
    
    const navContainer = document.getElementById('section-nav-grid');
    if (!navContainer) return;

    // Clear existing navigation
    navContainer.innerHTML = '';

    // Find all question cards
    const questionCards = document.querySelectorAll('.question-card[data-id]');

    questionCards.forEach(card => {
        const sectionId = card.getAttribute('data-id');
        const sectionTitle = getSectionTitle(sectionId);

        // Skip section 0
        if (sectionId && sectionId !== '0') {
            const navBtn = document.createElement('button');
            navBtn.className = 'nav-btn';
            navBtn.textContent = sectionId;
            navBtn.title = sectionTitle;
            navBtn.onclick = () => scrollToSection(sectionId);

            navContainer.appendChild(navBtn);
        }
    });
}

function scrollToSection(sectionId) {

    const element = document.getElementById('section-' + sectionId) ||
        document.querySelector(`[data-id="${sectionId}"]`);

    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });

        // Highlight the section temporarily
        element.style.border = '2px solid var(--accent-color)';
        element.style.borderRadius = '8px';

        setTimeout(() => {
            element.style.border = '';
            element.style.borderRadius = '';
        }, 2000);

        // Focus on the feedback textarea
        const textarea = element.querySelector('.feedback-text');
        if (textarea) {
            setTimeout(() => {
                textarea.focus();
            }, 500);
        }
    } else {
        console.warn('Section not found:', sectionId);
    }
}

function getSectionTitle(sectionId) {
    const element = document.querySelector(`[data-id="${sectionId}"]`);
    if (element) {
        const titleElement = element.querySelector('.section-title-only, .question-section-combined h3, h2, h3');
        if (titleElement) {
            return titleElement.textContent.trim();
        }
    }
    return `Section ${sectionId}`;
}

// ===========================================
// CHARACTER COUNTERS
// ===========================================

function initializeCharacterCounters() {

    // Only add counters for question-level sections, not comments
    document.querySelectorAll('.feedback-text[data-section-type="question"], .feedback-text[data-section-type="original_text"], .feedback-text[data-section-type="text_insertion"]').forEach(textarea => {
        const sectionId = textarea.id.replace('feedback-', '');

        // Update counter on input
        textarea.addEventListener('input', () => updateCharacterCounter(sectionId));

        // Initial count
        updateCharacterCounter(sectionId);
    });

    // For current implementation without section types, initialize all counters
    // This is a fallback for the current system
    if (document.querySelectorAll('.feedback-text[data-section-type]').length === 0) {
        document.querySelectorAll('.feedback-text').forEach(textarea => {
            const sectionId = textarea.id.replace('feedback-', '');

            // Update counter on input
            textarea.addEventListener('input', () => updateCharacterCounter(sectionId));

            // Initial count
            updateCharacterCounter(sectionId);
        });
    }
}

function updateCharacterCounter(sectionId) {
    const textarea = document.getElementById(`feedback-${sectionId}`);
    const counter = document.getElementById(`char-counter-${sectionId}`);

    if (textarea && counter) {
        const charCount = textarea.value.length;
        const wordCount = textarea.value.trim() ? textarea.value.trim().split(/\s+/).length : 0;
        counter.textContent = `${charCount} characters, ${wordCount} words`;
    }
}

// ===========================================
// TEMPLATE EDITOR FUNCTIONALITY
// ===========================================

function initializeTemplateEditor() {

    // Check if we're on the template editor page
    const templateContainer = document.getElementById('templates-container');
    if (!templateContainer) {
        return;
    }

    try {
        setupTemplateButtons();
        setupTabSwitching();
    } catch (error) {
        console.error('Error initializing template editor:', error);
    }
}

function setupTemplateButtons() {
    // Save individual template buttons
    document.querySelectorAll('.save-template-btn').forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const textarea = document.getElementById(`template-${id}`);

            if (textarea) {
                saveIndividualTemplate(id, textarea.value);
            }
        });
    });

    // Save all templates button
    const saveAllBtn = document.getElementById('save-all-templates');
    if (saveAllBtn) {
        saveAllBtn.addEventListener('click', saveAllTemplates);
    }
}

function setupTabSwitching() {
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', function () {
            const targetTab = this.getAttribute('data-target');

            // Remove active class from all tabs and panels
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

            // Add active class to clicked tab and corresponding panel
            this.classList.add('active');
            const targetPanel = document.getElementById(targetTab);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

function saveIndividualTemplate(id, content) {
    const data = {};
    data[id] = content;

    fetch('/save_templates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Template saved successfully!');
            } else {
                showToast('Error saving template: ' + (data.message || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error saving template:', error);
            showToast('Error saving template', 'error');
        });
}

function saveAllTemplates() {
    const templates = {};

    document.querySelectorAll('.template-input').forEach(textarea => {
        const id = textarea.id.replace('template-', '');
        templates[id] = textarea.value;
    });

    fetch('/save_templates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(templates)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('All templates saved successfully!');
            } else {
                showToast('Error saving templates: ' + (data.message || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error saving templates:', error);
            showToast('Error saving templates', 'error');
        });
}

// ===========================================
// UTILITY FUNCTIONS
// ===========================================

function showToast(message, type = 'success') {

    // Create or get toast container
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        background: ${type === 'error' ? 'var(--error-color)' : 'var(--success-color)'};
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;

    toastContainer.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 10);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

async function copyToClipboard(text) {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            textArea.remove();
        }
        return Promise.resolve();
    } catch (err) {
        console.error('Failed to copy text: ', err);
        return Promise.reject(err);
    }
}

// ===========================================
// TEMPLATE MANAGEMENT
// ===========================================

// Store original templates for reset functionality
function storeOriginalTemplates() {

    if (typeof window.originalTemplates === 'undefined') {
        window.originalTemplates = {};

        document.querySelectorAll('.feedback-text').forEach(textarea => {
            const id = textarea.id.replace('feedback-', '');
            window.originalTemplates[id] = textarea.value;
        });

    }
}

// Initialize original templates when review page loads
document.addEventListener('DOMContentLoaded', function () {
    if (document.querySelectorAll('.feedback-text').length > 0) {
        setTimeout(storeOriginalTemplates, 100);
    }
});

// ===========================================
// GLOBAL EXPORTS
// ===========================================

// Export functions for use in other scripts or HTML onclick handlers
window.toggleTheme = toggleTheme;
window.scrollToSection = scrollToSection;
window.insertCommentWithAnimation = insertCommentWithAnimation;
window.showToast = showToast;
window.copyToClipboard = copyToClipboard;

// Export dark mode API
window.DarkMode = {
    toggle: toggleTheme,
    setTheme: setTheme,
    getCurrentTheme: () => document.documentElement.getAttribute('data-theme') || 'light',
    forceTheme: (theme) => {
        if (theme === 'dark' || theme === 'light') {
            setTheme(theme);
            updateToggleButton(theme);
            localStorage.setItem('dmp-art-theme', theme);
        }
    }
};

