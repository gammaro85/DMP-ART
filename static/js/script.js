/**
 * DMP ART - Complete JavaScript Functionality
 * Enhanced with proper error handling, debugging, and responsive design
 */

// ===========================================
// SESSION MANAGEMENT
// ===========================================

/**
 * SessionManager - Handles review session persistence and restoration
 * Enables users to:
 * - Navigate freely between pages (Settings/Documentation) without losing progress
 * - Resume review after browser restart
 * - Auto-save feedback drafts every 30 seconds
 */
const SessionManager = {
    STORAGE_KEY: 'dmp-art-sessions',
    MAX_SESSIONS: 5,
    AUTO_SAVE_INTERVAL: 30000, // 30 seconds
    autoSaveTimer: null,

    /**
     * Save current review session to localStorage
     * @param {string} cacheId - UUID cache identifier
     * @param {string} filename - Original DMP filename
     * @param {Object} feedbackData - Current feedback text per section
     * @param {Object} metadata - Optional metadata (researcher name, etc.)
     */
    saveSession(cacheId, filename, feedbackData, metadata = {}) {
        if (!cacheId || !filename) {
            console.warn('SessionManager: Cannot save session without cacheId and filename');
            return false;
        }

        const sessions = this.getAllSessions();
        const timestamp = Date.now();

        // Find existing session or create new
        let sessionIndex = sessions.findIndex(s => s.sessionId === cacheId);

        const sessionData = {
            sessionId: cacheId,
            filename: filename,
            timestamp: sessionIndex >= 0 ? sessions[sessionIndex].timestamp : timestamp,
            lastSaved: timestamp,
            feedbackDraft: feedbackData,
            metadata: metadata
        };

        if (sessionIndex >= 0) {
            sessions[sessionIndex] = sessionData;
        } else {
            sessions.unshift(sessionData);
        }

        // Keep only MAX_SESSIONS most recent
        const trimmedSessions = sessions.slice(0, this.MAX_SESSIONS);

        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(trimmedSessions));
            console.log('SessionManager: Session saved', cacheId);
            return true;
        } catch (e) {
            console.error('SessionManager: Error saving session', e);
            return false;
        }
    },

    /**
     * Load session data from localStorage
     * @param {string} cacheId - Session identifier
     * @returns {Object|null} Session data or null if not found
     */
    loadSession(cacheId) {
        const sessions = this.getAllSessions();
        const session = sessions.find(s => s.sessionId === cacheId);

        if (session) {
            console.log('SessionManager: Session loaded', cacheId);
            return session;
        }

        console.log('SessionManager: No session found for', cacheId);
        return null;
    },

    /**
     * Get all saved sessions, sorted by last modified
     * @returns {Array} Array of session objects
     */
    getAllSessions() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('SessionManager: Error loading sessions', e);
            return [];
        }
    },

    /**
     * Get recent sessions for display on home page
     * @returns {Array} Up to MAX_SESSIONS recent sessions
     */
    getRecentSessions() {
        return this.getAllSessions()
            .sort((a, b) => b.lastSaved - a.lastSaved)
            .slice(0, this.MAX_SESSIONS);
    },

    /**
     * Delete a session from localStorage
     * @param {string} cacheId - Session to delete
     */
    deleteSession(cacheId) {
        const sessions = this.getAllSessions();
        const filtered = sessions.filter(s => s.sessionId !== cacheId);

        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered));
            console.log('SessionManager: Session deleted', cacheId);
            return true;
        } catch (e) {
            console.error('SessionManager: Error deleting session', e);
            return false;
        }
    },

    /**
     * Start auto-save timer for current review session
     */
    startAutoSave(cacheId, filename) {
        if (!cacheId || !filename) {
            console.warn('SessionManager: Cannot start auto-save without cacheId and filename');
            return;
        }

        // Clear existing timer
        this.stopAutoSave();

        console.log('SessionManager: Auto-save started');

        this.autoSaveTimer = setInterval(() => {
            const feedbackData = this.collectFeedbackData();
            const metadata = this.collectMetadata();

            if (Object.keys(feedbackData).length > 0) {
                this.saveSession(cacheId, filename, feedbackData, metadata);
                console.log('SessionManager: Auto-saved at', new Date().toLocaleTimeString());
            }
        }, this.AUTO_SAVE_INTERVAL);
    },

    /**
     * Stop auto-save timer
     */
    stopAutoSave() {
        if (this.autoSaveTimer) {
            clearInterval(this.autoSaveTimer);
            this.autoSaveTimer = null;
            console.log('SessionManager: Auto-save stopped');
        }
    },

    /**
     * Collect current feedback data from all textareas
     * @returns {Object} Section ID to feedback text mapping
     */
    collectFeedbackData() {
        const feedbackData = {};

        document.querySelectorAll('.feedback-text').forEach(textarea => {
            const sectionId = textarea.id.replace('feedback-', '');
            const value = textarea.value.trim();

            if (value) {
                feedbackData[sectionId] = value;
            }
        });

        return feedbackData;
    },

    /**
     * Collect metadata from page (researcher name, etc.)
     * @returns {Object} Metadata object
     */
    collectMetadata() {
        const metadata = {};

        // Try to extract researcher info from page if available
        const researcherSurnameEl = document.getElementById('researcher-surname');
        const researcherFirstnameEl = document.getElementById('researcher-firstname');

        if (researcherSurnameEl) metadata.researcher_surname = researcherSurnameEl.textContent;
        if (researcherFirstnameEl) metadata.researcher_firstname = researcherFirstnameEl.textContent;

        return metadata;
    },

    /**
     * Restore feedback data to textareas
     * @param {Object} feedbackData - Section ID to text mapping
     */
    restoreFeedbackData(feedbackData) {
        if (!feedbackData) return;

        Object.entries(feedbackData).forEach(([sectionId, text]) => {
            const textarea = document.getElementById(`feedback-${sectionId}`);
            if (textarea && !textarea.value) {
                textarea.value = text;
                console.log(`SessionManager: Restored feedback for section ${sectionId}`);
            }
        });
    },

    /**
     * Format session timestamp for display
     * @param {number} timestamp - Unix timestamp
     * @returns {string} Formatted date string
     */
    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minutes ago`;
        if (diffHours < 24) return `${diffHours} hours ago`;
        if (diffDays < 7) return `${diffDays} days ago`;

        return date.toLocaleDateString('pl-PL', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};

// ===========================================
// MAIN INITIALIZATION
// ===========================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('DMP ART: Initializing application...');

    try {
        // Initialize core functionality
        initializeDarkMode();
        initializeNavigation();
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
                    console.log('System theme changed to:', newTheme);
                }
            });
        }
    } catch (error) {
        console.error('Error setting up system theme listener:', error);
    }
}

// ===========================================
// NAVIGATION FUNCTIONALITY
// ===========================================

/**
 * Initialize standardized navigation
 * - Auto-detect current page
 * - Apply active states
 * - Conditionally enable Review link
 */
function initializeNavigation() {
    console.log('Initializing navigation...');

    try {
        const currentPage = document.body.getAttribute('data-page');
        if (!currentPage) {
            console.log('No data-page attribute found, skipping navigation initialization');
            return;
        }

        // Set active state for current page
        const navItems = document.querySelectorAll('.nav-item[data-page]');
        navItems.forEach(item => {
            const itemPage = item.getAttribute('data-page');

            if (itemPage === currentPage) {
                item.classList.add('active');

                // If it's a link, prevent navigation
                if (item.tagName === 'A') {
                    item.removeAttribute('href');
                }
            }
        });

        // Enable Review link if on review page OR if cache_id in URL
        const urlParams = new URLSearchParams(window.location.search);
        const reviewNavItem = document.querySelector('[data-page="review"]');

        if (reviewNavItem && (currentPage === 'review' || urlParams.has('cache_id'))) {
            // Convert disabled span to active link
            if (reviewNavItem.tagName === 'SPAN') {
                const reviewLink = document.createElement('a');
                reviewLink.href = window.location.pathname; // Use current path if already on review
                reviewLink.className = 'nav-item';
                reviewLink.setAttribute('data-page', 'review');
                reviewLink.textContent = 'Review';

                if (currentPage === 'review') {
                    reviewLink.classList.add('active');
                    reviewLink.removeAttribute('href');
                }

                reviewNavItem.replaceWith(reviewLink);
            }
        }

        console.log('Navigation initialized for page:', currentPage);
    } catch (error) {
        console.error('Error initializing navigation:', error);
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
        fileInfo: document.getElementById('file-info'),
        fileName: document.getElementById('file-name'),
        uploadBtn: document.getElementById('upload-btn'),
        clearBtn: document.getElementById('clear-btn')
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
        renderRecentSessions(); // NEW: Show recent review sessions

        console.log('Upload page initialized successfully');
    } catch (error) {
        console.error('Error initializing upload page:', error);
    }
}

/**
 * Render recent sessions on home page
 * Shows list of saved review sessions with continue/delete options
 */
function renderRecentSessions() {
    const container = document.getElementById('recent-sessions-container');
    const list = document.getElementById('recent-sessions-list');

    if (!container || !list) {
        console.log('Recent sessions container not found (not on index page)');
        return;
    }

    const sessions = SessionManager.getRecentSessions();

    if (sessions.length === 0) {
        container.classList.add('hidden');
        return;
    }

    // Show container
    container.classList.remove('hidden');

    // Clear existing content
    list.innerHTML = '';

    // Render each session
    sessions.forEach(session => {
        const item = document.createElement('div');
        item.className = 'session-item';

        const info = document.createElement('div');
        info.className = 'session-info';

        const filename = document.createElement('div');
        filename.className = 'session-filename';
        filename.textContent = session.filename;

        const meta = document.createElement('div');
        meta.className = 'session-meta';

        const timestamp = document.createElement('span');
        timestamp.innerHTML = `<i class="fas fa-clock"></i> ${SessionManager.formatTimestamp(session.lastSaved)}`;

        const feedbackCount = Object.keys(session.feedbackDraft || {}).length;
        const feedbackInfo = document.createElement('span');
        feedbackInfo.innerHTML = `<i class="fas fa-comment"></i> ${feedbackCount} section${feedbackCount !== 1 ? 's' : ''} with feedback`;

        meta.appendChild(timestamp);
        meta.appendChild(feedbackInfo);

        info.appendChild(filename);
        info.appendChild(meta);

        const actions = document.createElement('div');
        actions.className = 'session-actions';

        const continueBtn = document.createElement('button');
        continueBtn.className = 'session-btn continue';
        continueBtn.innerHTML = '<i class="fas fa-play"></i> Continue';
        continueBtn.onclick = () => continueSession(session);

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'session-btn delete';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.title = 'Delete session';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteSession(session.sessionId);
        };

        actions.appendChild(continueBtn);
        actions.appendChild(deleteBtn);

        item.appendChild(info);
        item.appendChild(actions);

        list.appendChild(item);
    });
}

/**
 * Continue a saved session
 * @param {Object} session - Session data
 */
function continueSession(session) {
    if (!session || !session.sessionId || !session.filename) {
        showToast('Invalid session data', 'error');
        return;
    }

    // Navigate to review page with cache_id
    const reviewUrl = `/review/${encodeURIComponent(session.filename)}?cache_id=${session.sessionId}`;
    window.location.href = reviewUrl;
}

/**
 * Delete a session with confirmation
 * @param {string} sessionId - Session ID to delete
 */
function deleteSession(sessionId) {
    const confirmed = confirm('Czy na pewno chcesz usunąć tę sesję?\n\nTa operacja jest nieodwracalna.');

    if (confirmed) {
        const success = SessionManager.deleteSession(sessionId);

        if (success) {
            showToast('Session deleted', 'success');
            renderRecentSessions(); // Refresh list
        } else {
            showToast('Error deleting session', 'error');
        }
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
    updateButtonStates(elements, 'file-selected');

    if (fileName) {
        fileName.textContent = file.name;
    }

    if (fileInfo) {
        fileInfo.classList.remove('hidden');
    }

    if (uploadBtn) {
        uploadBtn.disabled = false;
        uploadBtn.style.opacity = '1';
    }

    // Silent - visual feedback (filename display) is sufficient
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
            if (fileInfo) fileInfo.classList.add('hidden');
            if (fileName) fileName.textContent = '';

            // Silent - visual feedback (empty field) is sufficient
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

/**
 * Connect to Server-Sent Events endpoint for real-time progress updates
 * @param {string} sessionId - Unique session ID for this upload
 * @param {Function} onProgress - Callback for progress updates
 * @param {Function} onComplete - Callback when complete
 * @param {Function} onError - Callback for errors
 * @returns {EventSource} The event source connection
 */
function connectProgressStream(sessionId, onProgress, onComplete, onError) {
    const eventSource = new EventSource(`/progress/${sessionId}`);

    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Progress update:', data);

            if (data.status === 'complete') {
                onComplete(data);
                eventSource.close();
            } else if (data.status === 'error') {
                onError(data);
                eventSource.close();
            } else {
                onProgress(data);
            }
        } catch (error) {
            console.error('Error parsing progress data:', error);
        }
    };

    eventSource.onerror = function(error) {
        console.error('SSE connection error:', error);
        eventSource.close();
        onError({ message: 'Connection lost', progress: 0, status: 'error' });
    };

    return eventSource;
}

/**
 * Update progress bar UI with real-time data
 * @param {Object} data - Progress data from SSE
 */
function updateProgressBar(data) {
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const progressMessage = document.getElementById('progress-message');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressStatus = document.getElementById('progress-status');

    if (!progressContainer) return;

    // Show progress container
    progressContainer.classList.remove('hidden');

    // Update progress bar width
    if (progressFill) {
        progressFill.style.width = `${data.progress}%`;

        // Update color class based on progress
        progressFill.className = 'progress-fill';
        if (data.status === 'complete') {
            progressFill.classList.add('complete');
        } else if (data.progress < 30) {
            progressFill.classList.add('low', 'processing');
        } else if (data.progress < 70) {
            progressFill.classList.add('medium', 'processing');
        } else {
            progressFill.classList.add('high', 'processing');
        }
    }

    // Update message
    if (progressMessage) {
        progressMessage.textContent = data.message || 'Processing...';
    }

    // Update percentage
    if (progressPercentage) {
        progressPercentage.textContent = `${data.progress}%`;
    }

    // Update status
    if (progressStatus) {
        let statusText = '';
        switch (data.status) {
            case 'connected':
                statusText = 'Connected to server...';
                break;
            case 'processing':
                statusText = 'Processing your DMP file...';
                break;
            case 'complete':
                statusText = 'Processing complete! Redirecting...';
                break;
            case 'error':
                statusText = 'An error occurred during processing';
                break;
            default:
                statusText = 'Working...';
        }
        progressStatus.textContent = statusText;
    }
}

/**
 * Hide progress bar and reset
 */
function hideProgressBar() {
    const progressContainer = document.getElementById('progress-container');
    if (progressContainer) {
        progressContainer.classList.add('hidden');
    }

    // Reset progress bar
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        progressFill.style.width = '0%';
        progressFill.className = 'progress-fill';
    }
}

function uploadFile(file, elements) {
    const { loading, result, successMessage, errorMessage, errorText } = elements;

    console.log('Starting file upload:', file.name);

    const formData = new FormData();
    formData.append('file', file);

    // Hide previous results
    if (result) result.style.display = 'none';
    if (successMessage) successMessage.style.display = 'none';
    if (errorMessage) errorMessage.style.display = 'none';

    // Hide old loading, show progress bar instead
    if (loading) loading.style.display = 'none';

    // Start upload
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log('Upload response:', data);

            // Get session ID from response
            const sessionId = data.session_id;

            if (!sessionId) {
                // No session ID, handle as before (error case)
                hideProgressBar();

                if (errorMessage) {
                    errorMessage.style.display = 'block';
                }
                if (errorText) {
                    errorText.textContent = data.message || 'Unknown error occurred';
                }
                showToast(data.message || 'Upload failed', 'error');
                return;
            }

            // Connect to SSE for real-time progress
            let eventSource = connectProgressStream(
                sessionId,
                // On progress update
                (progressData) => {
                    updateProgressBar(progressData);
                },
                // On complete
                (completeData) => {
                    updateProgressBar(completeData);

                    // Show success message
                    showToast('File processed successfully!');

                    // Redirect after delay
                    setTimeout(() => {
                        if (completeData.redirect) {
                            window.location.href = completeData.redirect;
                        } else if (data.redirect) {
                            window.location.href = data.redirect;
                        }
                    }, 1500);
                },
                // On error
                (errorData) => {
                    hideProgressBar();

                    if (errorMessage) {
                        errorMessage.style.display = 'block';
                    }
                    if (errorText) {
                        errorText.textContent = errorData.message || 'Processing error occurred';
                    }
                    showToast(errorData.message || 'Processing failed', 'error');
                }
            );

        })
        .catch(error => {
            console.error('Upload error:', error);

            hideProgressBar();

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
        initializeAutoResize();
        initializeSessionManagement(); // NEW: Session persistence

        console.log('Review page initialized successfully');
    } catch (error) {
        console.error('Error initializing review page:', error);
    }
}

/**
 * Initialize session management for review page
 * - Restores saved feedback from localStorage
 * - Starts auto-save timer
 * - Sets up navigation warnings
 */
function initializeSessionManagement() {
    console.log('SessionManager: Initializing session management...');

    // Extract cache_id and filename from page
    const cacheId = getCacheIdFromPage();
    const filename = getFilenameFromPage();

    if (!cacheId || !filename) {
        console.warn('SessionManager: Cannot initialize - missing cache_id or filename');
        return;
    }

    console.log('SessionManager: Working with session', cacheId, filename);

    // Try to restore saved session
    const savedSession = SessionManager.loadSession(cacheId);
    if (savedSession && savedSession.feedbackDraft) {
        const hasUnsavedWork = Object.keys(SessionManager.collectFeedbackData()).length > 0;

        if (!hasUnsavedWork) {
            // Only restore if textareas are empty
            // Silent restore - filled textareas are visual confirmation
            SessionManager.restoreFeedbackData(savedSession.feedbackDraft);
        }
    }

    // Start auto-save
    SessionManager.startAutoSave(cacheId, filename);

    // Setup navigation warnings
    setupNavigationWarnings(cacheId, filename);

    // Save on page unload
    window.addEventListener('beforeunload', () => {
        const feedbackData = SessionManager.collectFeedbackData();
        const metadata = SessionManager.collectMetadata();
        SessionManager.saveSession(cacheId, filename, feedbackData, metadata);
    });
}

/**
 * Setup navigation warnings to prevent accidental data loss
 * - Home: warn if unsaved changes
 * - Settings/Documentation: safe (session auto-saved)
 * - Browser close: auto-save
 */
function setupNavigationWarnings(cacheId, filename) {
    // Intercept Home navigation link
    const homeLink = document.querySelector('a[data-page="index"], a[href="/"]');

    if (homeLink) {
        homeLink.addEventListener('click', (e) => {
            const feedbackData = SessionManager.collectFeedbackData();

            if (Object.keys(feedbackData).length > 0) {
                // Save session first
                const metadata = SessionManager.collectMetadata();
                SessionManager.saveSession(cacheId, filename, feedbackData, metadata);

                // Confirm navigation
                const confirmed = confirm(
                    'Nawigacja do strony głównej zakończy bieżącą sesję review.\n\n' +
                    'Twoje zmiany zostały zapisane i możesz je wznowić później.\n\n' +
                    'Czy na pewno chcesz przejść do strony głównej?'
                );

                if (!confirmed) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    // Settings/Documentation: Auto-save without warning
    const safeLinks = document.querySelectorAll(
        'a[data-page="settings"], a[href="/settings"], ' +
        'a[data-page="documentation"], a[href="/documentation"]'
    );

    safeLinks.forEach(link => {
        link.addEventListener('click', () => {
            const feedbackData = SessionManager.collectFeedbackData();
            const metadata = SessionManager.collectMetadata();
            SessionManager.saveSession(cacheId, filename, feedbackData, metadata);
            console.log('SessionManager: Session saved before navigation to', link.href);
        });
    });

    // Browser close/refresh: Auto-save
    window.addEventListener('beforeunload', (e) => {
        const feedbackData = SessionManager.collectFeedbackData();

        if (Object.keys(feedbackData).length > 0) {
            const metadata = SessionManager.collectMetadata();
            SessionManager.saveSession(cacheId, filename, feedbackData, metadata);

            // Show browser warning (only if there's unsaved work)
            e.preventDefault();
            e.returnValue = '';
        }
    });
}

/**
 * Extract cache_id from URL query parameter or page data
 * @returns {string|null} Cache ID
 */
function getCacheIdFromPage() {
    // Try URL parameter first
    const urlParams = new URLSearchParams(window.location.search);
    let cacheId = urlParams.get('cache_id');

    // Try data attribute on body/container
    if (!cacheId) {
        const container = document.querySelector('[data-cache-id]');
        cacheId = container ? container.getAttribute('data-cache-id') : null;
    }

    return cacheId;
}

/**
 * Extract filename from page
 * @returns {string|null} Filename
 */
function getFilenameFromPage() {
    // Try data attribute first
    const container = document.querySelector('[data-filename]');
    if (container) {
        return container.getAttribute('data-filename');
    }

    // Try to extract from page title or heading
    const heading = document.querySelector('h1, h2');
    if (heading) {
        const match = heading.textContent.match(/Review:\s*(.+?)$/i);
        if (match) return match[1].trim();
    }

    // Try from URL
    const pathMatch = window.location.pathname.match(/\/review\/(.+?)$/);
    if (pathMatch) return decodeURIComponent(pathMatch[1]);

    return null;
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
                // Silent - visual feedback (changed text) is sufficient
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
                // Silent - visual feedback (empty field) is sufficient
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
    // All DMP sections in order (based on dmp_structure.json)
    const allSections = ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2', '5.1', '5.2', '5.3', '5.4', '6.1', '6.2'];

    // Collect feedback for all sections
    const feedbackMap = {};
    document.querySelectorAll('.feedback-text').forEach(textarea => {
        const sectionId = textarea.id.replace('feedback-', '');
        feedbackMap[sectionId] = textarea.value.trim();
    });

    // Generate compiled feedback with full structure
    let compiled = '';

    allSections.forEach(sectionId => {
        const feedbackText = feedbackMap[sectionId];

        if (feedbackText) {
            compiled += `${sectionId} - ${feedbackText}\n\n`;
        } else {
            compiled += `${sectionId} brak komentarza\n\n`;
        }
    });

    return compiled.trim();
}

function saveFeedback() {
    const feedbackData = {};

    document.querySelectorAll('.feedback-text').forEach(textarea => {
        const sectionId = textarea.id.replace('feedback-', '');
        feedbackData[sectionId] = textarea.value;
    });

    // NEW: Save session to localStorage first
    const cacheId = getCacheIdFromPage();
    const filename = getFilenameFromPage();

    if (cacheId && filename) {
        const metadata = SessionManager.collectMetadata();
        SessionManager.saveSession(cacheId, filename, feedbackData, metadata);
        console.log('SessionManager: Session saved with feedback');
    }

    // Then save feedback file to server
    fetch('/save_feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cache_id: cacheId,
            filename: filename,
            feedback: compileFeedback(), // Save compiled feedback as text file
            feedbackData: feedbackData   // Also send raw data for potential future use
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Progress saved! You can safely navigate to Settings or other pages.', 'success');
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

        // Update counter on input with debouncing (300ms delay)
        const debouncedUpdate = debounce(() => updateCharacterCounter(sectionId), 300);
        textarea.addEventListener('input', debouncedUpdate);

        // Initial count
        updateCharacterCounter(sectionId);
    });

    // For current implementation without section types, initialize all counters
    // This is a fallback for the current system
    if (document.querySelectorAll('.feedback-text[data-section-type]').length === 0) {
        document.querySelectorAll('.feedback-text').forEach(textarea => {
            const sectionId = textarea.id.replace('feedback-', '');

            // Update counter on input with debouncing (300ms delay)
            const debouncedUpdate = debounce(() => updateCharacterCounter(sectionId), 300);
            textarea.addEventListener('input', debouncedUpdate);

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
// AUTO-RESIZE TEXTAREAS
// ===========================================

/**
 * Auto-resize a textarea to fit its content
 * @param {HTMLTextAreaElement} textarea - The textarea element to resize
 */
function autoResizeTextarea(textarea) {
    if (!textarea) return;

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';

    // Set height to scrollHeight plus a small buffer
    const newHeight = Math.max(textarea.scrollHeight, 80); // Minimum 80px height
    textarea.style.height = newHeight + 'px';
}

/**
 * Initialize auto-resize for all textareas on the page
 */
function initializeAutoResize() {
    console.log('Initializing auto-resize textareas...');

    // Get all feedback textareas
    const textareas = document.querySelectorAll('.feedback-text, .template-input, textarea');

    textareas.forEach(textarea => {
        // Set initial size
        autoResizeTextarea(textarea);

        // Add input event listener for auto-resize
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });

        // Also resize on focus (in case content was changed programmatically)
        textarea.addEventListener('focus', function() {
            autoResizeTextarea(this);
        });
    });

    console.log(`Auto-resize initialized for ${textareas.length} textareas`);
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
        initializeAutoResize();
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

/**
 * Debounce function to limit how often a function can fire
 * @param {Function} func - The function to debounce
 * @param {number} wait - The delay in milliseconds
 * @returns {Function} - The debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show notification - modal for errors, toast for info/success/warning
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'warning', 'info'
 */
function showToast(message, type = 'success') {
    console.log(`Notification (${type}):`, message);

    // Critical errors show as modal dialog
    if (type === 'error') {
        showModalDialog(message, type);
    } else {
        // Success/Info/Warning show as corner toast
        showCornerToast(message, type);
    }
}

/**
 * Show modal dialog for critical errors
 * @param {string} message - Message to display
 * @param {string} type - Type: 'error'
 */
function showModalDialog(message, type = 'error') {
    // Remove existing dialog if present
    const existingDialog = document.getElementById('notification-dialog');
    if (existingDialog) {
        existingDialog.remove();
    }

    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'notification-backdrop';
    backdrop.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.2s ease;
    `;

    // Icon and color for error
    const icon = '<i class="fas fa-times-circle"></i>';
    const color = 'var(--error-color)';

    // Create dialog
    const dialog = document.createElement('div');
    dialog.id = 'notification-dialog';
    dialog.className = 'notification-dialog';
    dialog.style.cssText = `
        background: var(--bg-card);
        border-radius: var(--border-radius-lg);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        padding: 2rem;
        max-width: 400px;
        width: 90%;
        text-align: center;
        transform: scale(0.9);
        opacity: 0;
        transition: transform 0.2s ease, opacity 0.2s ease;
    `;

    dialog.innerHTML = `
        <div style="font-size: 3rem; color: ${color}; margin-bottom: 1rem;">
            ${icon}
        </div>
        <div style="font-size: 1.1rem; color: var(--text-primary); margin-bottom: 1.5rem; line-height: 1.5;">
            ${message}
        </div>
        <button class="notification-ok-btn" style="
            background: ${color};
            color: white;
            border: none;
            border-radius: var(--border-radius-md);
            padding: 0.75rem 2rem;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 100px;
        ">OK</button>
    `;

    backdrop.appendChild(dialog);
    document.body.appendChild(backdrop);

    // Animate in
    requestAnimationFrame(() => {
        backdrop.style.opacity = '1';
        dialog.style.transform = 'scale(1)';
        dialog.style.opacity = '1';
    });

    // Close function
    const closeDialog = () => {
        backdrop.style.opacity = '0';
        dialog.style.transform = 'scale(0.9)';
        dialog.style.opacity = '0';
        setTimeout(() => {
            if (backdrop.parentNode) {
                backdrop.remove();
            }
        }, 200);
    };

    // OK button click
    const okBtn = dialog.querySelector('.notification-ok-btn');
    okBtn.addEventListener('click', closeDialog);

    // Hover effect for OK button
    okBtn.addEventListener('mouseenter', () => {
        okBtn.style.filter = 'brightness(1.1)';
        okBtn.style.transform = 'translateY(-1px)';
    });
    okBtn.addEventListener('mouseleave', () => {
        okBtn.style.filter = 'brightness(1)';
        okBtn.style.transform = 'translateY(0)';
    });

    // Click backdrop to close
    backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
            closeDialog();
        }
    });

    // ESC key to close
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeDialog();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

/**
 * Show corner toast notification (non-modal)
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'warning', 'info'
 */
function showCornerToast(message, type = 'success') {
    // Icon mapping
    const icons = {
        success: '<i class="fas fa-check-circle"></i>',
        warning: '<i class="fas fa-exclamation-triangle"></i>',
        info: '<i class="fas fa-info-circle"></i>'
    };

    // Color mapping
    const colors = {
        success: 'var(--success-color)',
        warning: 'var(--warning-color)',
        info: 'var(--primary-color)'
    };

    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 60px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 350px;
        `;
        document.body.appendChild(container);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `corner-toast toast-${type}`;

    const iconHtml = icons[type] || icons.info;
    const color = colors[type] || colors.info;

    toast.style.cssText = `
        background: var(--bg-card);
        border-left: 4px solid ${color};
        border-radius: var(--border-radius-md);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        transform: translateX(400px);
        opacity: 0;
        transition: all 0.3s ease;
        cursor: pointer;
    `;

    toast.innerHTML = `
        <div style="font-size: 1.25rem; color: ${color}; flex-shrink: 0;">
            ${iconHtml}
        </div>
        <div style="font-size: 0.9rem; color: var(--text-primary); line-height: 1.4; flex-grow: 1;">
            ${message}
        </div>
        <button style="
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 1.1rem;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        " aria-label="Close">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    });

    // Close function
    const closeToast = () => {
        toast.style.transform = 'translateX(400px)';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
            // Remove container if empty
            if (container.children.length === 0) {
                container.remove();
            }
        }, 300);
    };

    // Click to close
    toast.addEventListener('click', closeToast);

    // Close button
    const closeBtn = toast.querySelector('button');
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeToast();
    });

    // Auto-close after duration based on type
    const duration = type === 'warning' ? 7000 : 4000;
    setTimeout(closeToast, duration);
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
// AUTOSAVE FUNCTIONALITY
// ===========================================

const AUTOSAVE_INTERVAL = 30000; // 30 seconds
const AUTOSAVE_KEY_PREFIX = 'dmp-art-autosave-';
let autosaveTimer = null;

/**
 * Initialize autosave for review page
 */
function initializeAutosave() {
    console.log('Initializing autosave...');

    const feedbackTexts = document.querySelectorAll('.feedback-text');
    if (feedbackTexts.length === 0) {
        return;
    }

    // Get cache_id from URL or page
    const cacheId = getCacheId();
    if (!cacheId) {
        console.log('No cache_id found, autosave disabled');
        return;
    }

    // Try to restore from autosave
    restoreFromAutosave(cacheId);

    // Set up autosave on input with debounce
    feedbackTexts.forEach(textarea => {
        textarea.addEventListener('input', debounce(() => {
            saveToAutosave(cacheId);
        }, 2000)); // Save 2 seconds after last input
    });

    // Periodic autosave
    autosaveTimer = setInterval(() => {
        saveToAutosave(cacheId);
    }, AUTOSAVE_INTERVAL);

    // Save before leaving page
    window.addEventListener('beforeunload', () => {
        saveToAutosave(cacheId);
    });

    console.log('Autosave initialized for cache_id:', cacheId);
}

/**
 * Get cache_id from URL or data attribute
 */
function getCacheId() {
    const urlParams = new URLSearchParams(window.location.search);
    let cacheId = urlParams.get('cache_id');

    if (!cacheId) {
        const cacheIdElement = document.querySelector('[data-cache-id]');
        if (cacheIdElement) {
            cacheId = cacheIdElement.getAttribute('data-cache-id');
        }
    }

    return cacheId;
}

/**
 * Save feedback to localStorage
 */
function saveToAutosave(cacheId) {
    const feedbackData = {};
    let hasContent = false;

    document.querySelectorAll('.feedback-text').forEach(textarea => {
        const sectionId = textarea.id.replace('feedback-', '');
        const value = textarea.value.trim();
        if (value) {
            feedbackData[sectionId] = value;
            hasContent = true;
        }
    });

    if (hasContent) {
        const saveData = {
            feedback: feedbackData,
            timestamp: Date.now(),
            url: window.location.href
        };

        try {
            localStorage.setItem(AUTOSAVE_KEY_PREFIX + cacheId, JSON.stringify(saveData));
            updateAutosaveIndicator('saved');
        } catch (e) {
            console.error('Autosave failed:', e);
        }
    }
}

/**
 * Restore feedback from localStorage
 */
function restoreFromAutosave(cacheId) {
    const savedData = localStorage.getItem(AUTOSAVE_KEY_PREFIX + cacheId);

    if (!savedData) {
        return false;
    }

    try {
        const data = JSON.parse(savedData);
        const feedback = data.feedback;
        const timestamp = data.timestamp;

        // Check if saved data is less than 24 hours old
        const hoursSinceSave = (Date.now() - timestamp) / (1000 * 60 * 60);
        if (hoursSinceSave > 24) {
            localStorage.removeItem(AUTOSAVE_KEY_PREFIX + cacheId);
            return false;
        }

        // Check if any feedback areas are currently empty
        let hasEmptyFeedback = false;
        document.querySelectorAll('.feedback-text').forEach(textarea => {
            if (!textarea.value.trim()) {
                hasEmptyFeedback = true;
            }
        });

        if (!hasEmptyFeedback) {
            return false; // Don't overwrite existing content
        }

        // Ask user if they want to restore
        const saveTime = new Date(timestamp).toLocaleString();
        if (confirm(`Znaleziono autozapis z ${saveTime}. Czy przywrócić?`)) {
            Object.entries(feedback).forEach(([sectionId, value]) => {
                const textarea = document.getElementById(`feedback-${sectionId}`);
                if (textarea && !textarea.value.trim()) {
                    textarea.value = value;
                    updateCharacterCounter(sectionId);
                }
            });
            // Silent restore - filled textareas are visual confirmation
            return true;
        }
    } catch (e) {
        console.error('Error restoring autosave:', e);
    }

    return false;
}

/**
 * Update autosave indicator in UI
 */
function updateAutosaveIndicator(status) {
    let indicator = document.getElementById('autosave-indicator');

    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'autosave-indicator';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 20px;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.8rem;
            z-index: 1000;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(indicator);
    }

    if (status === 'saved') {
        indicator.textContent = '✓ Autozapis';
        indicator.style.backgroundColor = 'var(--success-color)';
        indicator.style.color = 'white';
        indicator.style.opacity = '1';

        setTimeout(() => {
            indicator.style.opacity = '0';
        }, 2000);
    }
}

/**
 * Clear autosave for current document
 */
function clearAutosave() {
    const cacheId = getCacheId();
    if (cacheId) {
        localStorage.removeItem(AUTOSAVE_KEY_PREFIX + cacheId);
    }
}

// ===========================================
// DMP HISTORY FUNCTIONALITY
// ===========================================

const HISTORY_KEY = 'dmp-art-history';
const MAX_HISTORY_ITEMS = 20;

/**
 * Add current DMP to history
 */
function addToHistory(filename, cacheId) {
    const history = getHistory();

    const newEntry = {
        filename: filename,
        cacheId: cacheId,
        timestamp: Date.now(),
        url: window.location.href
    };

    // Remove duplicate if exists
    const filteredHistory = history.filter(item => item.cacheId !== cacheId);

    // Add new entry at the beginning
    filteredHistory.unshift(newEntry);

    // Keep only last MAX_HISTORY_ITEMS
    const trimmedHistory = filteredHistory.slice(0, MAX_HISTORY_ITEMS);

    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmedHistory));
}

/**
 * Get DMP history
 */
function getHistory() {
    try {
        const history = localStorage.getItem(HISTORY_KEY);
        return history ? JSON.parse(history) : [];
    } catch (e) {
        return [];
    }
}

/**
 * Render history dropdown in navigation
 */
function renderHistoryDropdown() {
    const historyContainer = document.getElementById('history-dropdown');
    if (!historyContainer) return;

    const history = getHistory();

    if (history.length === 0) {
        historyContainer.innerHTML = '<div class="no-history">Brak historii</div>';
        return;
    }

    const html = history.map(item => {
        const date = new Date(item.timestamp);
        const dateStr = date.toLocaleDateString('pl-PL');
        const timeStr = date.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' });

        return `
            <a href="${item.url}" class="history-item" title="${item.filename}">
                <span class="history-filename">${item.filename.substring(0, 30)}${item.filename.length > 30 ? '...' : ''}</span>
                <span class="history-date">${dateStr} ${timeStr}</span>
            </a>
        `;
    }).join('');

    historyContainer.innerHTML = html;
}

// ===========================================
// COMMENT SEARCH FUNCTIONALITY
// ===========================================

/**
 * Initialize comment search
 */
function initializeCommentSearch() {
    const searchContainer = document.querySelector('.quick-comments-pane');
    if (!searchContainer) return;

    // Check if search already exists
    if (document.getElementById('comment-search-input')) return;

    // Create search input
    const searchHtml = `
        <div class="comment-search-wrapper" style="margin-bottom: 8px;">
            <input type="text"
                   id="comment-search-input"
                   placeholder="Szukaj komentarzy..."
                   style="width: 100%; padding: 6px 8px; font-size: 0.75rem; border: 1px solid var(--border-light); border-radius: 4px; background: var(--bg-secondary); color: var(--text-primary);">
        </div>
    `;

    // Insert search before the comments list
    const commentsListHeader = searchContainer.querySelector('h3');
    if (commentsListHeader) {
        commentsListHeader.insertAdjacentHTML('afterend', searchHtml);
    }

    // Add search event listener
    const searchInput = document.getElementById('comment-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            filterComments(this.value.toLowerCase());
        }, 200));
    }
}

/**
 * Filter comments based on search term
 */
function filterComments(searchTerm) {
    const commentItems = document.querySelectorAll('.quick-comment-item, .category-comment-item');

    commentItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (!searchTerm || text.includes(searchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// ===========================================
// COMMENT USAGE STATISTICS (TAG CLOUD)
// ===========================================

const COMMENT_STATS_KEY = 'dmp-art-comment-stats';

/**
 * Track comment usage
 */
function trackCommentUsage(commentName) {
    const stats = getCommentStats();
    stats[commentName] = (stats[commentName] || 0) + 1;
    localStorage.setItem(COMMENT_STATS_KEY, JSON.stringify(stats));
}

/**
 * Get comment usage statistics
 */
function getCommentStats() {
    try {
        const stats = localStorage.getItem(COMMENT_STATS_KEY);
        return stats ? JSON.parse(stats) : {};
    } catch (e) {
        return {};
    }
}

/**
 * Initialize tag cloud for quick comments
 */
function initializeTagCloud() {
    const quickCommentsPane = document.querySelector('.quick-comments-pane');
    if (!quickCommentsPane) return;

    const stats = getCommentStats();
    if (Object.keys(stats).length === 0) return;

    // Find or create tag cloud container
    let tagCloudContainer = document.getElementById('comment-tag-cloud');
    if (!tagCloudContainer) {
        tagCloudContainer = document.createElement('div');
        tagCloudContainer.id = 'comment-tag-cloud';
        tagCloudContainer.className = 'tag-cloud-container';
        tagCloudContainer.style.cssText = `
            margin-bottom: 12px;
            padding: 8px;
            background: var(--bg-tertiary);
            border-radius: 4px;
            border: 1px solid var(--border-light);
        `;

        const header = document.createElement('div');
        header.style.cssText = 'font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 6px;';
        header.textContent = 'Często używane:';
        tagCloudContainer.appendChild(header);

        const tagsWrapper = document.createElement('div');
        tagsWrapper.id = 'tag-cloud-tags';
        tagsWrapper.style.cssText = 'display: flex; flex-wrap: wrap; gap: 4px;';
        tagCloudContainer.appendChild(tagsWrapper);

        // Insert after search (if exists) or after h3
        const searchWrapper = quickCommentsPane.querySelector('.comment-search-wrapper');
        if (searchWrapper) {
            searchWrapper.after(tagCloudContainer);
        } else {
            const h3 = quickCommentsPane.querySelector('h3');
            if (h3) h3.after(tagCloudContainer);
        }
    }

    renderTagCloud(stats);
}

/**
 * Render tag cloud based on usage stats
 */
function renderTagCloud(stats) {
    const tagsWrapper = document.getElementById('tag-cloud-tags');
    if (!tagsWrapper) return;

    // Sort by usage count and take top 10
    const sortedStats = Object.entries(stats)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    if (sortedStats.length === 0) {
        tagsWrapper.innerHTML = '<span style="font-size: 0.7rem; color: var(--text-secondary);">Brak statystyk</span>';
        return;
    }

    // Calculate font sizes based on usage
    const maxCount = sortedStats[0][1];
    const minCount = sortedStats[sortedStats.length - 1][1];
    const fontRange = { min: 0.65, max: 0.9 }; // rem

    const html = sortedStats.map(([name, count]) => {
        let fontSize = fontRange.min;
        if (maxCount > minCount) {
            fontSize = fontRange.min + ((count - minCount) / (maxCount - minCount)) * (fontRange.max - fontRange.min);
        }

        return `
            <span class="tag-cloud-item"
                  data-comment-name="${escapeHtml(name)}"
                  style="font-size: ${fontSize}rem; padding: 2px 6px; background: var(--primary-color); color: white; border-radius: 3px; cursor: pointer; white-space: nowrap;"
                  title="Użyto ${count} razy">
                ${escapeHtml(name.substring(0, 20))}${name.length > 20 ? '...' : ''}
            </span>
        `;
    }).join('');

    tagsWrapper.innerHTML = html;

    // Add click handlers to tags
    tagsWrapper.querySelectorAll('.tag-cloud-item').forEach(tag => {
        tag.addEventListener('click', function() {
            const commentName = this.getAttribute('data-comment-name');
            const commentItem = document.querySelector(`.quick-comment-item[data-name="${commentName}"]`);
            if (commentItem) {
                commentItem.click();
            }
        });
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===========================================
// ENHANCED INITIALIZATION
// ===========================================

// Initialize new features when review page loads
document.addEventListener('DOMContentLoaded', function () {
    // Initialize autosave on review page
    if (document.querySelectorAll('.feedback-text').length > 0) {
        setTimeout(() => {
            initializeAutosave();
            initializeCommentSearch();
            initializeTagCloud();

            // Track comment usage when comments are clicked
            document.querySelectorAll('.quick-comment-item').forEach(item => {
                item.addEventListener('click', function() {
                    const name = this.getAttribute('data-name') || this.textContent.trim().substring(0, 30);
                    trackCommentUsage(name);
                    // Update tag cloud after use
                    setTimeout(initializeTagCloud, 100);
                });
            });

            // Add current DMP to history
            const filename = document.querySelector('[data-filename]')?.getAttribute('data-filename');
            const cacheId = getCacheId();
            if (filename && cacheId) {
                addToHistory(filename, cacheId);
            }
        }, 200);
    }

    // Render history dropdown if it exists
    renderHistoryDropdown();
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
window.trackCommentUsage = trackCommentUsage;
window.getCommentStats = getCommentStats;
window.getHistory = getHistory;
window.clearAutosave = clearAutosave;

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

// Export Autosave API
window.Autosave = {
    save: () => saveToAutosave(getCacheId()),
    clear: clearAutosave,
    getCacheId: getCacheId
};

// Export History API
window.DMPHistory = {
    get: getHistory,
    add: addToHistory,
    render: renderHistoryDropdown
};

// ===========================================
// HISTORY MODAL - Session Archive Management
// ===========================================

const HistoryModal = {
    modal: null,
    closeBtn: null,
    activeSessions: null,
    archivedSessions: null,

    init() {
        this.modal = document.getElementById('history-modal');
        this.closeBtn = document.querySelector('.history-modal-close');
        this.activeSessions = document.getElementById('active-sessions-list');
        this.archivedSessions = document.getElementById('archived-sessions-list');

        if (!this.modal) return;

        const historyBtn = document.querySelector('.history-btn');
        if (historyBtn) {
            historyBtn.addEventListener('click', () => this.open());
        }

        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.close());
        }

        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) this.close();
        });

        ArchiveViewModal.init();
    },

    open() {
        if (!this.modal) return;
        this.modal.classList.add('active');
        this.loadSessions();
    },

    close() {
        if (!this.modal) return;
        this.modal.classList.remove('active');
    },

    async loadSessions() {
        await Promise.all([this.loadActiveSessions(), this.loadArchivedSessions()]);
    },

    async loadActiveSessions() {
        if (!this.activeSessions) return;
        const sessions = SessionManager.getAllSessions();
        const sessionIds = sessions.map(s => s.sessionId);
        try {
            const response = await fetch('/api/get-active-sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_ids: sessionIds })
            });
            const data = await response.json();
            if (data.success && data.active_sessions.length > 0) {
                this.renderActiveSessions(data.active_sessions);
            } else {
                this.activeSessions.innerHTML = '<div class="history-empty">Brak aktywnych sesji</div>';
            }
        } catch (error) {
            console.error('Error loading active sessions:', error);
            this.activeSessions.innerHTML = '<div class="history-empty">Błąd ładowania sesji</div>';
        }
    },

    async loadArchivedSessions() {
        if (!this.archivedSessions) return;
        try {
            const response = await fetch('/api/get-archived-sessions');
            const data = await response.json();
            if (data.success && data.archives.length > 0) {
                this.renderArchivedSessions(data.archives);
            } else {
                this.archivedSessions.innerHTML = '<div class="history-empty">Brak zarchiwizowanych sesji</div>';
            }
        } catch (error) {
            console.error('Error loading archived sessions:', error);
            this.archivedSessions.innerHTML = '<div class="history-empty">Błąd ładowania archiwum</div>';
        }
    },

    _getDisplayName(session) {
        if (session.session_name) return session.session_name;
        if (session.researcher_surname) {
            return session.researcher_surname + (session.researcher_firstname ? ' ' + session.researcher_firstname : '');
        }
        return session.filename || session.filename_original || 'Sesja bez nazwy';
    },

    renderActiveSessions(sessions) {
        const html = sessions.map(session => {
            const displayName = this._getDisplayName(session);
            const date = session.creation_date || '';
            const sessionIdEsc = session.session_id.replace(/'/g, "\\'");
            const nameEsc = displayName.replace(/'/g, "\\'").replace(/"/g, '&quot;');
            return `
                <div class="session-item" data-session-id="${session.session_id}">
                    <div class="session-info">
                        <div class="session-title" id="stitle-active-${session.session_id}">${displayName}</div>
                        <div class="session-meta">
                            ${date ? `<span><i class="fas fa-calendar"></i> ${date}</span>` : ''}
                            <span><i class="fas fa-file"></i> ${session.filename || ''}</span>
                        </div>
                        <div id="srename-active-${session.session_id}" style="display:none"></div>
                    </div>
                    <div class="session-actions">
                        <button class="session-action-btn btn-rename" onclick="HistoryModal.showRenameForm('${sessionIdEsc}', '${nameEsc}', 'active')">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                        <button class="session-action-btn btn-view" onclick="HistoryModal.openSession('${sessionIdEsc}')">
                            <i class="fas fa-eye"></i> Otwórz
                        </button>
                    </div>
                </div>`;
        }).join('');
        this.activeSessions.innerHTML = `<div class="session-list">${html}</div>`;
    },

    renderArchivedSessions(archives) {
        const html = archives.map(archive => {
            const displayName = this._getDisplayName(archive);
            const archivedDate = archive.archived_date ? new Date(archive.archived_date).toLocaleString('pl-PL') : '';
            const archiveIdEsc = archive.archive_id.replace(/'/g, "\\'");
            const nameEsc = displayName.replace(/'/g, "\\'").replace(/"/g, '&quot;');
            return `
                <div class="session-item" data-archive-id="${archive.archive_id}">
                    <div class="session-info">
                        <div class="session-title" id="stitle-archive-${archive.archive_id}">${displayName}</div>
                        <div class="session-meta">
                            ${archivedDate ? `<span><i class="fas fa-archive"></i> ${archivedDate}</span>` : ''}
                            <span><i class="fas fa-file"></i> ${archive.filename_original || ''}</span>
                        </div>
                        <div id="srename-archive-${archive.archive_id}" style="display:none"></div>
                    </div>
                    <div class="session-actions">
                        <button class="session-action-btn btn-rename" onclick="HistoryModal.showRenameForm('${archiveIdEsc}', '${nameEsc}', 'archive')">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                        <button class="session-action-btn btn-view" onclick="HistoryModal.viewArchive('${archiveIdEsc}')">
                            <i class="fas fa-eye"></i> Podgląd
                        </button>
                        <button class="session-action-btn btn-delete" onclick="HistoryModal.deleteArchive('${archiveIdEsc}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>`;
        }).join('');
        this.archivedSessions.innerHTML = `<div class="session-list">${html}</div>`;
    },

    showRenameForm(sessionId, currentName, sessionType) {
        const formContainerId = `srename-${sessionType}-${sessionId}`;
        const titleId = `stitle-${sessionType}-${sessionId}`;
        const container = document.getElementById(formContainerId);
        const titleEl = document.getElementById(titleId);
        if (!container) return;

        const isVisible = container.style.display !== 'none';
        if (isVisible) {
            container.style.display = 'none';
            return;
        }

        container.innerHTML = `
            <div class="session-rename-form">
                <input type="text" id="rename-input-${sessionId}" value="${currentName.replace(/"/g, '&quot;')}" placeholder="Nazwa sesji..." maxlength="120">
                <button class="btn-confirm" onclick="HistoryModal.saveRename('${sessionId}', '${sessionType}')"><i class="fas fa-check"></i></button>
                <button class="btn-cancel" onclick="document.getElementById('srename-${sessionType}-${sessionId}').style.display='none'"><i class="fas fa-times"></i></button>
            </div>`;
        container.style.display = 'block';

        const input = document.getElementById(`rename-input-${sessionId}`);
        if (input) {
            input.focus();
            input.select();
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.saveRename(sessionId, sessionType);
                if (e.key === 'Escape') container.style.display = 'none';
            });
        }
    },

    async saveRename(sessionId, sessionType) {
        const input = document.getElementById(`rename-input-${sessionId}`);
        if (!input) return;
        const newName = input.value.trim();

        try {
            const response = await fetch('/api/rename-session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, session_type: sessionType, session_name: newName })
            });
            const data = await response.json();
            if (data.success) {
                const titleEl = document.getElementById(`stitle-${sessionType}-${sessionId}`);
                if (titleEl) titleEl.textContent = newName || sessionId;
                const container = document.getElementById(`srename-${sessionType}-${sessionId}`);
                if (container) container.style.display = 'none';
                if (typeof showToast === 'function') showToast('Nazwa zapisana', 'success');
            } else {
                if (typeof showToast === 'function') showToast('Błąd: ' + data.message, 'error');
            }
        } catch (error) {
            if (typeof showToast === 'function') showToast('Błąd połączenia', 'error');
        }
    },

    openSession(sessionId) {
        window.location.href = `/review?cache_id=${sessionId}`;
    },

    async viewArchive(archiveId) {
        try {
            const response = await fetch(`/api/restore-archived-session/${archiveId}`);
            const data = await response.json();
            if (data.success) {
                ArchiveViewModal.show(data);
            } else {
                if (typeof showToast === 'function') showToast('Błąd: ' + data.message, 'error');
                else alert('Błąd: ' + data.message);
            }
        } catch (error) {
            if (typeof showToast === 'function') showToast('Błąd połączenia: ' + error.message, 'error');
        }
    },

    async deleteArchive(archiveId) {
        if (!confirm('Czy na pewno chcesz usunąć to archiwum? Tej operacji nie można cofnąć.')) return;
        try {
            const response = await fetch(`/api/delete-archived-session/${archiveId}`, { method: 'DELETE' });
            const data = await response.json();
            if (data.success) {
                const item = document.querySelector(`[data-archive-id="${archiveId}"]`);
                if (item) item.remove();
                if (this.archivedSessions.querySelectorAll('.session-item').length === 0) {
                    this.archivedSessions.innerHTML = '<div class="history-empty">Brak zarchiwizowanych sesji</div>';
                }
                if (typeof showToast === 'function') showToast('Archiwum usunięte', 'success');
            } else {
                if (typeof showToast === 'function') showToast('Błąd: ' + data.message, 'error');
            }
        } catch (error) {
            if (typeof showToast === 'function') showToast('Błąd połączenia', 'error');
        }
    }
};

// ===========================================
// ARCHIVE VIEW MODAL
// ===========================================
const SECTION_LABELS = {
    '1.1': '1.1 Opis i zbiór danych',
    '1.2': '1.2 Standardy i metadane',
    '2.1': '2.1 Prawa własności i licencje',
    '2.2': '2.2 Ograniczenia dostępu',
    '3.1': '3.1 Przechowywanie i backup',
    '3.2': '3.2 Bezpieczeństwo danych',
    '4.1': '4.1 Wymagania prawne',
    '4.2': '4.2 Ochrona danych osobowych',
    '5.1': '5.1 Udostępnianie danych',
    '5.2': '5.2 Długoterminowe przechowywanie',
    '5.3': '5.3 Licencje na dane',
    '5.4': '5.4 Wybór repozytorium',
    '6.1': '6.1 Odpowiedzialności',
    '6.2': '6.2 Zasoby i koszty'
};

const ArchiveViewModal = {
    modal: null,

    init() {
        const existing = document.getElementById('archive-view-modal');
        if (existing) { this.modal = existing; this._bindClose(); return; }

        const el = document.createElement('div');
        el.id = 'archive-view-modal';
        el.innerHTML = `
            <div class="archive-view-content">
                <div class="archive-view-header">
                    <div class="archive-view-title-group">
                        <h2 id="avm-title"><i class="fas fa-archive"></i> Podgląd archiwum</h2>
                        <div class="archive-view-meta" id="avm-meta"></div>
                    </div>
                    <button class="archive-view-close" id="avm-close">&times;</button>
                </div>
                <div class="archive-view-body" id="avm-body"></div>
                <div class="archive-view-actions">
                    <button class="session-action-btn btn-view" id="avm-copy-btn">
                        <i class="fas fa-copy"></i> Kopiuj komentarze
                    </button>
                    <button class="session-action-btn btn-rename" id="avm-close-btn">
                        <i class="fas fa-times"></i> Zamknij
                    </button>
                </div>
            </div>`;
        document.body.appendChild(el);
        this.modal = el;
        this._bindClose();
    },

    _bindClose() {
        const closeBtn = document.getElementById('avm-close');
        const closeBtnFooter = document.getElementById('avm-close-btn');
        if (closeBtn) closeBtn.addEventListener('click', () => this.hide());
        if (closeBtnFooter) closeBtnFooter.addEventListener('click', () => this.hide());
        this.modal.addEventListener('click', (e) => { if (e.target === this.modal) this.hide(); });

        const copyBtn = document.getElementById('avm-copy-btn');
        if (copyBtn) copyBtn.addEventListener('click', () => this._copyFeedback());
    },

    show(data) {
        const { metadata, feedback } = data;
        const titleEl = document.getElementById('avm-title');
        const metaEl = document.getElementById('avm-meta');
        const bodyEl = document.getElementById('avm-body');
        if (!titleEl || !metaEl || !bodyEl) return;

        const displayName = metadata.session_name
            || (metadata.researcher_surname ? `${metadata.researcher_surname} ${metadata.researcher_firstname || ''}`.trim() : '')
            || metadata.filename_original
            || 'Archiwum';

        titleEl.innerHTML = `<i class="fas fa-archive"></i> ${displayName}`;

        const archivedDate = metadata.archived_date ? new Date(metadata.archived_date).toLocaleString('pl-PL') : '';
        metaEl.innerHTML = [
            metadata.filename_original ? `<span><i class="fas fa-file"></i> ${metadata.filename_original}</span>` : '',
            archivedDate ? `<span><i class="fas fa-calendar"></i> Zarchiwizowano: ${archivedDate}</span>` : '',
            metadata.competition_name ? `<span><i class="fas fa-trophy"></i> ${metadata.competition_name}</span>` : ''
        ].filter(Boolean).join('');

        const sections = feedback.sections || {};
        const allSectionIds = ['1.1','1.2','2.1','2.2','3.1','3.2','4.1','4.2','5.1','5.2','5.3','5.4','6.1','6.2'];

        bodyEl.innerHTML = allSectionIds.map(id => {
            const text = sections[id] || '';
            const label = SECTION_LABELS[id] || id;
            return `
                <div class="archive-view-section">
                    <div class="archive-view-section-header">
                        <span>${label}</span>
                        ${text ? '' : '<span style="font-weight:400;color:var(--text-muted);font-size:0.8rem">brak komentarza</span>'}
                    </div>
                    <div class="archive-view-section-body">
                        ${text
                            ? `<div class="feedback-text">${text.replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>`
                            : '<div class="no-feedback">—</div>'}
                    </div>
                </div>`;
        }).join('');

        this.modal.classList.add('active');
        this._currentFeedback = feedback;
    },

    hide() {
        if (this.modal) this.modal.classList.remove('active');
    },

    _copyFeedback() {
        if (!this._currentFeedback) return;
        const compiled = this._currentFeedback.compiled_feedback
            || Object.entries(this._currentFeedback.sections || {})
                .map(([id, text]) => `${SECTION_LABELS[id] || id}\n${text}`)
                .join('\n\n');
        if (!compiled) return;
        navigator.clipboard.writeText(compiled).then(() => {
            if (typeof showToast === 'function') showToast('Skopiowano do schowka', 'success');
        }).catch(() => {
            if (typeof showToast === 'function') showToast('Błąd kopiowania', 'error');
        });
    }
};

// Initialize History Modal when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    HistoryModal.init();
});

window.HistoryModal = HistoryModal;
window.ArchiveViewModal = ArchiveViewModal;

console.log('DMP ART script.js loaded successfully (v0.9.1 with archive system)');