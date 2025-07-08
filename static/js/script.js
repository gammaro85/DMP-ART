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
        showThemeNotification(newTheme);
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
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#121212' : '#ffffff');
        }
    } catch (error) {
        console.error('Error setting theme:', error);
    }
}

function updateToggleButton(theme) {
    try {
        const themeIcon = document.getElementById('theme-icon');
        const themeText = document.getElementById('theme-text');

        if (themeIcon && themeText) {
            if (theme === 'dark') {
                themeIcon.textContent = '☀️';
                themeText.textContent = 'Light Mode';
            } else {
                themeIcon.textContent = '🌙';
                themeText.textContent = 'Dark Mode';
            }
        }
    } catch (error) {
        console.error('Error updating toggle button:', error);
    }
}

function showThemeNotification(theme) {
    try {
        // Try to use existing toast system first
        if (typeof showToast === 'function') {
            const message = theme === 'dark' ? '🌙 Dark mode enabled' : '☀️ Light mode enabled';
            showToast(message);
            return;
        }

        // Fallback notification
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 12px 24px;
            border-radius: 8px;
            box-shadow: var(--shadow);
            z-index: 10000;
            border: 1px solid var(--border-medium);
            font-size: 14px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        const message = theme === 'dark' ? '🌙 Dark mode enabled' : '☀️ Light mode enabled';
        notification.textContent = message;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
        }, 10);

        // Remove after 2 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 2000);
    } catch (error) {
        console.error('Error showing theme notification:', error);
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
        downloadLink: document.getElementById('download-link'),
        reviewLink: document.getElementById('review-link'),
        newUploadBtn: document.getElementById('new-upload-btn'),
        tryAgainBtn: document.getElementById('try-again-btn')
    };

    // Exit if not on upload page
    if (!elements.dropArea) {
        console.log('Not on upload page, skipping upload initialization');
        return;
    }

    console.log('Upload page elements found, setting up functionality...');

    try {
        setupDragAndDrop(elements);
        setupFileSelection(elements);
        setupUploadButton(elements);
        setupUtilityButtons(elements);

        console.log('Upload page initialized successfully');
    } catch (error) {
        console.error('Error initializing upload page:', error);
    }
}

function setupDragAndDrop(elements) {
    const { dropArea } = elements;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop area when dragging file over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.add('highlight');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.remove('highlight');
        }, false);
    });

    // Handle dropped files
    dropArea.addEventListener('drop', function (e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFiles(files, elements);
        }
    }, false);
}

function setupFileSelection(elements) {
    const { selectFileBtn, fileInput } = elements;

    if (selectFileBtn && fileInput) {
        selectFileBtn.addEventListener('click', function () {
            fileInput.click();
        });

        fileInput.addEventListener('change', function () {
            if (fileInput.files.length > 0) {
                handleFiles(fileInput.files, elements);
            }
        });
    }
}

function setupUploadButton(elements) {
    const { uploadBtn, fileInput } = elements;

    if (uploadBtn) {
        uploadBtn.addEventListener('click', function () {
            if (!fileInput || fileInput.files.length === 0) {
                showError('Please select a file first.', elements);
                return;
            }

            const file = fileInput.files[0];
            if (validateFile(file)) {
                uploadFile(file, elements);
            } else {
                showError('Invalid file. Please select a valid PDF or DOCX file.', elements);
            }
        });
    }
}

function setupUtilityButtons(elements) {
    const { clearBtn, newUploadBtn, tryAgainBtn } = elements;

    if (clearBtn) {
        clearBtn.addEventListener('click', () => resetForm(elements));
    }

    if (newUploadBtn) {
        newUploadBtn.addEventListener('click', () => {
            resetForm(elements);
            hideResults(elements);
        });
    }

    if (tryAgainBtn) {
        tryAgainBtn.addEventListener('click', () => {
            resetForm(elements);
            hideResults(elements);
        });
    }
}

function handleFiles(files, elements) {
    console.log('Handling files:', files.length);

    const file = files[0];

    console.log('File details:', {
        name: file.name,
        type: file.type,
        size: file.size,
        sizeKB: Math.round(file.size / 1024),
        sizeMB: Math.round(file.size / (1024 * 1024) * 100) / 100
    });

    if (!validateFile(file)) {
        return;
    }

    // Display file info
    const { fileName, fileInfo } = elements;
    if (fileName) {
        fileName.textContent = file.name;
    }
    if (fileInfo) {
        fileInfo.classList.remove('hidden');
    }

    // Hide any previous results
    hideResults(elements);

    console.log('File ready for upload:', file.name);
}

function validateFile(file) {
    const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    // Check file type
    if (!allowedTypes.includes(file.type)) {
        const typeError = `Invalid file type: ${file.type || 'unknown'}. Please select a PDF or DOCX file.`;
        console.error(typeError);
        showError(typeError);
        return false;
    }

    // Check file size (16MB limit)
    const maxSize = 16 * 1024 * 1024; // 16MB in bytes
    if (file.size > maxSize) {
        const sizeError = `File too large: ${(file.size / (1024 * 1024)).toFixed(2)}MB. Maximum size is 16MB.`;
        console.error(sizeError);
        showError(sizeError);
        return false;
    }

    console.log('File validation passed');
    return true;
}

function uploadFile(file, elements) {
    console.log('Starting file upload:', file.name);

    const { fileInfo, loading } = elements;
    const formData = new FormData();
    formData.append('file', file);

    // Show loading state
    if (fileInfo) fileInfo.classList.add('hidden');
    if (loading) loading.classList.remove('hidden');

    // Create XMLHttpRequest for better control
    const xhr = new XMLHttpRequest();

    // Set up timeout (5 minutes)
    const uploadTimeout = setTimeout(() => {
        xhr.abort();
        if (loading) loading.classList.add('hidden');
        showError('Upload timed out after 5 minutes. Please try again with a smaller file.', elements);
        console.error('Upload timeout');
    }, 5 * 60 * 1000);

    // Track upload progress
    xhr.upload.addEventListener('progress', function (e) {
        if (e.lengthComputable) {
            const percentComplete = Math.round((e.loaded / e.total) * 100);
            console.log(`Upload progress: ${percentComplete}%`);

            // Update loading text if element exists
            const loadingText = loading?.querySelector('p');
            if (loadingText) {
                loadingText.textContent = `Processing file... ${percentComplete}%`;
            }
        }
    });

    // Handle successful response
    xhr.onload = function () {
        clearTimeout(uploadTimeout);

        if (loading) loading.classList.add('hidden');

        console.log('Upload completed with status:', xhr.status);
        console.log('Response text:', xhr.responseText);

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                console.log('Parsed response:', response);

                if (response.success) {
                    showSuccess(response, elements);
                } else {
                    showError(response.message || 'Processing failed', elements);
                }
            } catch (e) {
                console.error('Error parsing response:', e);
                showError('Server returned invalid response. Please try again.', elements);
            }
        } else {
            console.error('HTTP error:', xhr.status);
            showError(`Server error (Status: ${xhr.status}). Please try again.`, elements);
        }
    };

    // Handle network errors
    xhr.onerror = function () {
        clearTimeout(uploadTimeout);
        if (loading) loading.classList.add('hidden');
        console.error('Network error during upload');
        showError('Network error. Please check your connection and try again.', elements);
    };

    // Handle aborted uploads
    xhr.onabort = function () {
        clearTimeout(uploadTimeout);
        if (loading) loading.classList.add('hidden');
        console.log('Upload aborted');
    };

    // Send the request
    xhr.open('POST', '/upload');
    xhr.send(formData);
}

function showSuccess(response, elements) {
    console.log('Upload successful');

    const { result, successMessage, errorMessage, downloadLink, reviewLink } = elements;

    if (result) result.classList.remove('hidden');
    if (successMessage) successMessage.classList.remove('hidden');
    if (errorMessage) errorMessage.classList.add('hidden');

    // Set up download and review links
    if (downloadLink && response.download_url) {
        downloadLink.href = response.download_url;
    }
    if (reviewLink && response.review_url) {
        reviewLink.href = response.review_url;
    }
}

function showError(message, elements = {}) {
    console.log('Showing error:', message);

    const { result, successMessage, errorMessage, errorText, fileInfo, fileInput } = elements;

    if (result) result.classList.remove('hidden');
    if (successMessage) successMessage.classList.add('hidden');
    if (errorMessage) errorMessage.classList.remove('hidden');
    if (errorText) errorText.textContent = message;

    // Show file info again so user can try again
    if (fileInfo && fileInput && fileInput.files.length > 0) {
        fileInfo.classList.remove('hidden');
    }
}

function resetForm(elements) {
    console.log('Resetting form');

    const { fileInput, fileName, fileInfo, loading } = elements;

    if (fileInput) fileInput.value = '';
    if (fileName) fileName.textContent = '';
    if (fileInfo) fileInfo.classList.add('hidden');
    if (loading) loading.classList.add('hidden');
}

function hideResults(elements) {
    const { result, successMessage, errorMessage } = elements;

    if (result) result.classList.add('hidden');
    if (successMessage) successMessage.classList.add('hidden');
    if (errorMessage) errorMessage.classList.add('hidden');
}

// ===========================================
// REVIEW PAGE FUNCTIONALITY
// ===========================================

function initializeReviewPage() {
    console.log('Initializing review page...');

    const elements = {
        commentButtons: document.querySelectorAll('.comment-btn'),
        copyButtons: document.querySelectorAll('.copy-btn'),
        resetButtons: document.querySelectorAll('.reset-btn'),
        clearButtons: document.querySelectorAll('.clear-btn'),
        compileButton: document.getElementById('compile-btn'),
        saveFeedbackButton: document.getElementById('save-feedback-btn'),
        compiledContainer: document.getElementById('compiled-feedback-container'),
        compiledTextarea: document.getElementById('compiled-feedback'),
        copyCompiledButton: document.getElementById('copy-compiled-btn'),
        downloadFeedbackButton: document.getElementById('download-feedback-btn'),
        closeCompiledButton: document.getElementById('close-compiled-btn')
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

    document.querySelectorAll('.feedback-text').forEach(textarea => {
        const sectionId = textarea.id.replace('feedback-', '');

        // Update counter on input
        textarea.addEventListener('input', () => updateCharacterCounter(sectionId));

        // Initial count
        updateCharacterCounter(sectionId);
    });
}

function updateCharacterCounter(sectionId) {
    const textarea = document.getElementById(`feedback-${sectionId}`);
    const counter = document.getElementById(`char-counter-${sectionId}`);

    if (textarea && counter) {
        const charCount = textarea.value.length;
        const wordCount = textarea.value.trim().split(/\s+/).filter(word => word.length > 0).length;

        counter.textContent = `${charCount} characters, ${wordCount} words`;
    }
}

// ===========================================
// TEMPLATE EDITOR FUNCTIONALITY
// ===========================================

function initializeTemplateEditor() {
    console.log('Initializing template editor...');

    const elements = {
        saveTemplateButtons: document.querySelectorAll('.save-template-btn'),
        saveAllTemplatesButton: document.getElementById('save-all-templates'),
        tabButtons: document.querySelectorAll('.tab-btn'),
        tabPanels: document.querySelectorAll('.tab-panel')
    };

    // Exit if not on template editor page
    if (!elements.saveTemplateButtons.length && !elements.saveAllTemplatesButton && !elements.tabButtons.length) {
        console.log('Not on template editor page, skipping template editor initialization');
        return;
    }

    try {
        setupTabNavigation(elements);
        setupTemplateSaving(elements);

        console.log('Template editor initialized successfully');
    } catch (error) {
        console.error('Error initializing template editor:', error);
    }
}

function setupTabNavigation(elements) {
    const { tabButtons, tabPanels } = elements;

    tabButtons.forEach(button => {
        button.addEventListener('click', function () {
            // Remove active class from all buttons and panels
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanels.forEach(panel => panel.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Show corresponding panel
            const tabId = this.getAttribute('data-tab');
            const targetPanel = document.getElementById(`${tabId}-panel`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

function setupTemplateSaving(elements) {
    const { saveTemplateButtons, saveAllTemplatesButton } = elements;

    // Individual save buttons
    saveTemplateButtons.forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const templateInput = document.getElementById(`template-${id}`);

            if (templateInput) {
                const data = {};
                data[id] = templateInput.value;
                saveToServer('/save_templates', data);
            }
        });
    });

    // Save all button
    if (saveAllTemplatesButton) {
        saveAllTemplatesButton.addEventListener('click', function () {
            const templates = {};

            document.querySelectorAll('.template-item').forEach(item => {
                const id = item.getAttribute('data-id');
                const templateInput = document.getElementById(`template-${id}`);

                if (templateInput) {
                    templates[id] = templateInput.value;
                }
            });

            saveToServer('/save_templates', templates);
        });
    }
}

function saveToServer(endpoint, data) {
    console.log('Saving to server:', endpoint, data);

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showToast('Saved successfully!');
            } else {
                showToast('Error: ' + (result.message || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            showToast('Error saving data', 'error');
        });
}

// ===========================================
// UTILITY FUNCTIONS
// ===========================================

function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        return new Promise((resolve, reject) => {
            try {
                const textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                resolve();
            } catch (error) {
                reject(error);
            }
        });
    }
}

function showToast(message, type = 'success') {
    console.log(`Toast: ${message} (${type})`);

    // Try to find existing toast element
    let toast = document.querySelector('.success-toast');

    // Create toast if it doesn't exist
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'success-toast';
        document.body.appendChild(toast);
    }

    // Set message and type
    toast.textContent = message;
    toast.className = 'success-toast';

    if (type === 'error') {
        toast.classList.add('error');
    }

    // Show the toast
    toast.classList.add('show');

    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
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

// Store original templates for reset functionality
function storeOriginalTemplates() {
    if (!window.originalTemplates) {
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