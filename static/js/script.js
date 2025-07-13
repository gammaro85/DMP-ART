/**
 * DMP ART - Complete JavaScript Functionality
 * Enhanced with proper error handling, debugging, and responsive design
 */

// ===========================================
// MAIN INITIALIZATION
// ===========================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('DMP ART: Initializing application...');

    try {
        // Initialize core functionality
        initializeDarkMode();
        initializeUploadPage();
        initializeReviewPage();
        initializeTemplateEditor();

        console.log('DMP ART: All components initialized successfully');
    } catch (error) {
        console.error('DMP ART: Error during initialization:', error);
    }
});

// ===========================================
// DARK MODE FUNCTIONALITY
// ===========================================

function initializeDarkMode() {
    console.log('Initializing dark mode...');

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

        console.log('Dark mode initialized with theme:', initialTheme);
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

        console.log('Theme toggled to:', newTheme);
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

        if (themeText) {
            if (theme === 'dark') {
                themeText.textContent = 'Light Mode';
            } else {
                themeText.textContent = 'Dark Mode';
            }
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
                    console.log('System theme changed to:', newTheme);
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
    console.log('Initializing upload page...');

    // Get all required elements
    const elements = {
        dropArea: document.getElementById('drop-area'),
        fileInput: document.getElementById('file-input'),
        selectFileBtn: document.getElementById('select-file-btn'),
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
        console.log('Not on upload page, skipping upload initialization');
        return;
    }

    try {
        setupDragAndDrop(elements);
        setupFileSelection(elements);
        setupUploadButton(elements);
        setupClearButton(elements);

        console.log('Upload page initialized successfully');
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
    const { fileInput, selectFileBtn } = elements;

    if (selectFileBtn) {
        selectFileBtn.addEventListener('click', () => {
            if (fileInput) fileInput.click();
        });
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

    console.log('File selected:', file.name);

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
        uploadBtn.addEventListener('click', () => {
            if (elements.selectedFile) {
                uploadFile(elements.selectedFile, elements);
            } else {
                showToast('Please select a file first', 'error');
            }
        });
    }
}

function setupClearButton(elements) {
    const { clearBtn, fileInput, fileInfo, fileName, uploadBtn } = elements;

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            elements.selectedFile = null;

            if (fileInput) fileInput.value = '';
            if (fileInfo) fileInfo.style.display = 'none';
            if (fileName) fileName.textContent = '';
            if (uploadBtn) {
                uploadBtn.disabled = true;
                uploadBtn.style.opacity = '0.6';
            }

            showToast('File cleared');
        });
    }
}

function uploadFile(file, elements) {
    const { loading, result, successMessage, errorMessage, errorText } = elements;

    console.log('Starting file upload:', file.name);

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
            console.log('Upload response:', data);

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
    console.log('Initializing review page...');

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
        console.log('Not on review page, skipping review initialization');
        return;
    }

    try {
        initializeSectionNavigation();
        setupCommentButtons(elements);
        setupFeedbackButtons(elements);
        setupCompileButton(elements);
        setupSaveFeedbackButton(elements);
        initializeCharacterCounters();

        console.log('Review page initialized successfully');
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

    console.log(`Comment inserted into section ${id}`);
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
    console.log('Initializing section navigation...');

    try {
        createSectionNavigation();
        console.log('Section navigation initialized');
    } catch (error) {
        console.error('Error initializing section navigation:', error);
    }
}

function createSectionNavigation() {
    const navContainer = document.getElementById('section-nav');
    if (!navContainer) return;

    // Clear existing navigation
    navContainer.innerHTML = '';

    // Find all question cards
    const questionCards = document.querySelectorAll('.question-card[data-id]');

    questionCards.forEach(card => {
        const sectionId = card.getAttribute('data-id');
        const sectionTitle = getSectionTitle(sectionId);

        if (sectionId) {
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
    console.log('Scrolling to section:', sectionId);

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
    console.log('Initializing character counters...');

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
    console.log('Initializing template editor...');

    // Check if we're on the template editor page
    const templateContainer = document.getElementById('templates-container');
    if (!templateContainer) {
        console.log('Not on template editor page, skipping template editor initialization');
        return;
    }

    try {
        setupTemplateButtons();
        setupTabSwitching();
        console.log('Template editor initialized successfully');
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
    console.log(`Toast (${type}):`, message);

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
    console.log('Storing original templates...');

    if (typeof window.originalTemplates === 'undefined') {
        window.originalTemplates = {};

        document.querySelectorAll('.feedback-text').forEach(textarea => {
            const id = textarea.id.replace('feedback-', '');
            window.originalTemplates[id] = textarea.value;
        });

        console.log('Original templates stored:', Object.keys(window.originalTemplates));
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

console.log('DMP ART script.js loaded successfully');