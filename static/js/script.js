// static/js/script.js

// Global variables
let window_dmpFilename = '';

// Toast notification function
function showToast(message, type = 'success') {
    // Remove any existing toast
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    // Add styles
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        font-size: 14px;
        max-width: 300px;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;

    document.body.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 100);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Copy text to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
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
        return new Promise((res, rej) => {
            document.execCommand('copy') ? res() : rej();
            textArea.remove();
        });
    }
}

// Initialize functionality based on page
document.addEventListener('DOMContentLoaded', function () {
    // Initialize page-specific functionality
    initializeUploadPage();
    initializeReviewPage();
    initializeTemplateEditor();
});

// UPLOAD PAGE FUNCTIONALITY
function initializeUploadPage() {
    const form = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const submitBtn = document.getElementById('submit-btn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    if (!form) return; // Exit if not on upload page

    // File input change handler
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file && submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = `Upload ${file.name}`;
            }
        });
    }

    // Form submit handler
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            uploadFile();
        });
    }

    function uploadFile() {
        const formData = new FormData();
        const file = fileInput.files[0];

        if (!file) {
            showError('Please select a file to upload.');
            return;
        }

        formData.append('file', file);

        // Show loading state
        if (loading) {
            loading.classList.remove('hidden');
        }
        if (result) {
            result.classList.add('hidden');
        }
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
        }

        // Set upload timeout (60 seconds)
        const uploadTimeout = setTimeout(() => {
            if (loading) {
                loading.classList.add('hidden');
            }
            showError('Upload timeout. The file might be too large or the server is busy.');
        }, 60000);

        const xhr = new XMLHttpRequest();

        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                clearTimeout(uploadTimeout);
                if (loading) {
                    loading.classList.add('hidden');
                }
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Upload File';
                }

                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            window.location.href = '/review?file=' + encodeURIComponent(response.filename);
                        } else {
                            showError(response.message || 'An error occurred during processing.');
                        }
                    } catch (e) {
                        showError('Invalid response from server.');
                        console.error('Error parsing response:', e);
                    }
                } else {
                    showError('Server error: ' + xhr.status);
                    console.error('Server error:', xhr.status);
                }
            }
        };

        xhr.onerror = function () {
            clearTimeout(uploadTimeout);
            if (loading) {
                loading.classList.add('hidden');
            }
            showError('Network error. Please try again.');
            console.error('Network error');
        };

        xhr.open('POST', '/upload');
        xhr.send(formData);
    }

    function showError(message) {
        if (result) {
            result.classList.remove('hidden');
        }
        if (successMessage) {
            successMessage.classList.add('hidden');
        }
        if (errorMessage) {
            errorMessage.classList.remove('hidden');
        }
        if (errorText) {
            errorText.textContent = message;
        }
    }
}

// REVIEW PAGE FUNCTIONALITY
function initializeReviewPage() {
    // Get all interactive elements
    const commentButtons = document.querySelectorAll('.comment-btn');
    const copyButtons = document.querySelectorAll('.copy-btn');
    const resetButtons = document.querySelectorAll('.reset-btn');
    const compileButton = document.getElementById('compile-btn');
    const compiledContainer = document.getElementById('compiled-feedback-container');
    const compiledTextarea = document.getElementById('compiled-feedback');
    const copyCompiledButton = document.getElementById('copy-compiled-btn');
    const downloadFeedbackButton = document.getElementById('download-feedback-btn');
    const closeCompiledButton = document.getElementById('close-compiled-btn');
    const saveFeedbackButton = document.getElementById('save-feedback-btn');

    if (!commentButtons.length && !compileButton) return; // Exit if not on review page

    // Initialize navigation functionality
    initializeSectionNavigation();

    // Original template text for reset functionality
    const originalTemplates = {};

    // Initialize original templates
    document.querySelectorAll('.feedback-text').forEach(textarea => {
        const id = textarea.id.replace('feedback-', '');
        originalTemplates[id] = textarea.value;
    });

    // Handle comment button clicks
    if (commentButtons) {
        commentButtons.forEach(button => {
            button.addEventListener('click', function () {
                const id = this.getAttribute('data-id');
                const comment = this.getAttribute('data-comment');
                insertComment(id, comment);
            });
        });
    }

    // Insert comment into feedback textarea
    function insertComment(id, comment) {
        const textarea = document.getElementById(`feedback-${id}`);
        if (!textarea) return;

        // Get current cursor position
        const startPos = textarea.selectionStart;
        const endPos = textarea.selectionEnd;

        // Insert comment at cursor position or at the end
        if (startPos !== undefined && endPos !== undefined) {
            // Add a newline if not at the beginning of the textarea
            const prefix = startPos > 0 && textarea.value.charAt(startPos - 1) !== '\n' ? '\n' : '';

            // Add the comment
            textarea.value =
                textarea.value.substring(0, startPos) +
                prefix + comment + '\n' +
                textarea.value.substring(endPos);

            // Set cursor position after inserted comment
            const newPos = startPos + prefix.length + comment.length + 1;
            textarea.selectionStart = newPos;
            textarea.selectionEnd = newPos;
        } else {
            // If no cursor position, append to the end
            const prefix = textarea.value.length > 0 && textarea.value.charAt(textarea.value.length - 1) !== '\n' ? '\n' : '';
            textarea.value += prefix + comment + '\n';
        }

        // Focus the textarea and trigger change event
        textarea.focus();
        textarea.dispatchEvent(new Event('input'));

        // Show feedback with animation
        showToast('Comment added successfully!');
    }

    // Handle copy button clicks
    if (copyButtons) {
        copyButtons.forEach(button => {
            button.addEventListener('click', function () {
                const id = this.getAttribute('data-id');
                const textarea = document.getElementById(`feedback-${id}`);
                if (textarea && textarea.value.trim()) {
                    copyToClipboard(textarea.value)
                        .then(() => showToast('Copied to clipboard!'))
                        .catch(() => showToast('Failed to copy to clipboard', 'error'));
                } else {
                    showToast('No feedback to copy', 'error');
                }
            });
        });
    }

    // Handle reset button clicks
    if (resetButtons) {
        resetButtons.forEach(button => {
            button.addEventListener('click', function () {
                const id = this.getAttribute('data-id');
                const textarea = document.getElementById(`feedback-${id}`);
                if (textarea && originalTemplates[id] !== undefined) {
                    if (confirm('Are you sure you want to reset this feedback to the original template?')) {
                        textarea.value = originalTemplates[id];
                        textarea.dispatchEvent(new Event('input'));
                        showToast('Feedback reset to original template');
                    }
                }
            });
        });
    }

    // Handle compile button click
    if (compileButton) {
        compileButton.addEventListener('click', function () {
            compileAllFeedback();
        });
    }

    // Handle compiled feedback actions
    if (copyCompiledButton) {
        copyCompiledButton.addEventListener('click', function () {
            if (compiledTextarea) {
                copyToClipboard(compiledTextarea.value)
                    .then(() => showToast('Report copied to clipboard!'))
                    .catch(() => showToast('Failed to copy to clipboard', 'error'));
            }
        });
    }

    if (downloadFeedbackButton) {
        downloadFeedbackButton.addEventListener('click', function () {
            if (compiledTextarea) {
                downloadFeedback(compiledTextarea.value);
            }
        });
    }

    if (closeCompiledButton) {
        closeCompiledButton.addEventListener('click', function () {
            if (compiledContainer) {
                compiledContainer.classList.add('hidden');
            }
        });
    }

    // Handle save feedback button
    if (saveFeedbackButton) {
        saveFeedbackButton.addEventListener('click', function () {
            saveAllFeedback();
        });
    }

    // Compile all feedback into a report
    function compileAllFeedback() {
        let compiledText = '# DMP Feedback Report\n\n';
        compiledText += `Generated on: ${new Date().toLocaleDateString()}\n\n`;

        const feedbackTextareas = document.querySelectorAll('.feedback-text');
        let hasContent = false;

        feedbackTextareas.forEach(textarea => {
            const sectionId = textarea.id.replace('feedback-', '');
            const questionCard = document.querySelector(`[data-id="${sectionId}"]`);

            if (questionCard && textarea.value.trim()) {
                const questionElement = questionCard.querySelector('.question-section-combined strong');
                const questionText = questionElement ? questionElement.textContent : `Section ${sectionId}`;

                compiledText += `## ${questionText}\n\n`;
                compiledText += `${textarea.value.trim()}\n\n`;
                compiledText += '---\n\n';
                hasContent = true;
            }
        });

        if (!hasContent) {
            showToast('No feedback content to compile', 'error');
            return;
        }

        if (compiledTextarea) {
            compiledTextarea.value = compiledText;
        }
        if (compiledContainer) {
            compiledContainer.classList.remove('hidden');
        }
    }

    // Save all feedback to server
    function saveAllFeedback() {
        const feedbackData = {};
        const feedbackTextareas = document.querySelectorAll('.feedback-text');

        feedbackTextareas.forEach(textarea => {
            const sectionId = textarea.id.replace('feedback-', '');
            feedbackData[sectionId] = textarea.value;
        });

        const urlParams = new URLSearchParams(window.location.search);
        const filename = urlParams.get('file');

        if (!filename) {
            showToast('No filename found for saving feedback', 'error');
            return;
        }

        const data = {
            filename: filename,
            feedback: feedbackData
        };

        fetch('/save_feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Feedback saved successfully!');
                } else {
                    showToast(`Error: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                showToast(`Error: ${error.message}`, 'error');
            });
    }

    // Download feedback as text file
    function downloadFeedback(text) {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `DMP_Feedback_${new Date().toISOString().slice(0, 10)}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
}

// SECTION NAVIGATION FUNCTIONALITY
function initializeSectionNavigation() {
    // Find all question cards and create navigation
    const questionCards = document.querySelectorAll('.question-card');
    const navContainer = document.getElementById('section-nav');

    if (!navContainer || questionCards.length === 0) return;

    // Clear existing navigation
    navContainer.innerHTML = '';

    questionCards.forEach(card => {
        const sectionId = card.getAttribute('data-id');
        const questionElement = card.querySelector('.question-section-combined strong');

        if (sectionId && questionElement) {
            const navBtn = document.createElement('button');
            navBtn.className = 'nav-btn';
            navBtn.textContent = sectionId;
            navBtn.title = questionElement.textContent;
            navBtn.onclick = () => scrollToSection(sectionId);

            navContainer.appendChild(navBtn);
        }
    });
}

// Enhanced scroll to section function
function scrollToSection(sectionId) {
    const element = document.getElementById('section-' + sectionId) ||
        document.querySelector(`[data-id="${sectionId}"]`);

    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Highlight the section temporarily
        element.style.border = '2px solid var(--accent-color)';
        element.style.borderRadius = '8px';

        setTimeout(() => {
            element.style.border = '';
            element.style.borderRadius = '';
        }, 2000);

        // Focus on the feedback textarea for this section
        const textarea = element.querySelector('.feedback-text');
        if (textarea) {
            setTimeout(() => {
                textarea.focus();
            }, 500);
        }
    }
}

// TEMPLATE EDITOR FUNCTIONALITY
function initializeTemplateEditor() {
    // Get template editor elements
    const saveTemplateButtons = document.querySelectorAll('.save-template-btn');
    const saveAllTemplatesButton = document.getElementById('save-all-templates');

    if (!saveTemplateButtons.length && !saveAllTemplatesButton) return; // Exit if not on template editor page

    // Handle individual save buttons
    if (saveTemplateButtons) {
        saveTemplateButtons.forEach(button => {
            button.addEventListener('click', function () {
                const id = this.getAttribute('data-id');
                const templateInput = document.getElementById(`template-${id}`);

                if (templateInput) {
                    saveTemplate(id, templateInput.value);
                }
            });
        });
    }

    // Handle save all button
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

            saveAllTemplates(templates);
        });
    }

    // Function to save a single template
    function saveTemplate(id, text) {
        const data = {};
        data[id] = text;

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
                    showToast(`Error: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                showToast(`Error: ${error.message}`, 'error');
            });
    }

    // Function to save all templates
    function saveAllTemplates(templates) {
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
                    showToast(`Error: ${data.message}`, 'error');
                }
            })
            .catch(error => {
                showToast(`Error: ${error.message}`, 'error');
            });
    }
}