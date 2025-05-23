// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // UPLOAD PAGE FUNCTIONALITY
    var dropArea = document.getElementById('drop-area');
    var fileInput = document.getElementById('file-input');
    var selectFileBtn = document.getElementById('select-file-btn');
    var fileInfo = document.getElementById('file-info');
    var fileName = document.getElementById('file-name');
    var uploadBtn = document.getElementById('upload-btn');
    var clearBtn = document.getElementById('clear-btn');
    var loading = document.getElementById('loading');
    var result = document.getElementById('result');
    var successMessage = document.getElementById('success-message');
    var errorMessage = document.getElementById('error-message');
    var errorText = document.getElementById('error-text');
    var downloadLink = document.getElementById('download-link');
    var reviewLink = document.getElementById('review-link');
    var newUploadBtn = document.getElementById('new-upload-btn');
    var tryAgainBtn = document.getElementById('try-again-btn');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function(eventName) {
        if (dropArea) {
            dropArea.addEventListener(eventName, preventDefaults, false);
        }
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop area when dragging file over it
    ['dragenter', 'dragover'].forEach(function(eventName) {
        if (dropArea) {
            dropArea.addEventListener(eventName, highlight, false);
        }
    });
    
    ['dragleave', 'drop'].forEach(function(eventName) {
        if (dropArea) {
            dropArea.addEventListener(eventName, unhighlight, false);
        }
    });
    
    function highlight() {
        if (dropArea) {
            dropArea.classList.add('highlight');
        }
    }
    
    function unhighlight() {
        if (dropArea) {
            dropArea.classList.remove('highlight');
        }
    }
    
    // Handle dropped files
    if (dropArea) {
        dropArea.addEventListener('drop', handleDrop, false);
    }
    
    function handleDrop(e) {
        var dt = e.dataTransfer;
        var files = dt.files;
        
        if (files.length > 0) {
            handleFiles(files);
        }
    }
    
    // Handle selected files
    if (selectFileBtn) {
        selectFileBtn.addEventListener('click', function() {
            if (fileInput) {
                fileInput.click();
            }
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                handleFiles(fileInput.files);
            }
        });
    }
    
    function handleFiles(files) {
        var file = files[0];
        
        // Validate file type
        if (!file.type || file.type !== 'application/pdf') {
            showError('Please select a PDF file.');
            return;
        }
        
        // Validate file size (max 16MB)
        if (file.size > 16 * 1024 * 1024) {
            showError('File is too large. Maximum size is 16MB.');
            return;
        }
        
        // Display file info
        if (fileName) {
            fileName.textContent = file.name;
        }
        if (fileInfo) {
            fileInfo.classList.remove('hidden');
        }
    }
    
    // Handle upload button
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            if (!fileInput || fileInput.files.length === 0) {
                showError('Please select a file first.');
                return;
            }
            
            var file = fileInput.files[0];
            
            // Validate file again before upload
            if (file.type !== 'application/pdf') {
                showError('Please select a PDF file.');
                return;
            }
            
            uploadFile(file);
        });
    }
    
    // Handle clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            resetForm();
        });
    }
    
    // Handle new upload button
    if (newUploadBtn) {
        newUploadBtn.addEventListener('click', function() {
            resetForm();
            if (result) {
                result.classList.add('hidden');
            }
            if (fileInfo) {
                fileInfo.classList.add('hidden');
            }
        });
    }
    
    // Handle try again button
    if (tryAgainBtn) {
        tryAgainBtn.addEventListener('click', function() {
            resetForm();
            if (result) {
                result.classList.add('hidden');
            }
        });
    }
    
    function resetForm() {
        if (fileInput) {
            fileInput.value = '';
        }
        if (fileName) {
            fileName.textContent = '';
        }
        if (fileInfo) {
            fileInfo.classList.add('hidden');
        }
    }
    
    function uploadFile(file) {
        var formData = new FormData();
        formData.append('file', file);
        
        // Show loading spinner
        if (fileInfo) {
            fileInfo.classList.add('hidden');
        }
        if (loading) {
            loading.classList.remove('hidden');
        }
        
        // Set up upload timeout
        var uploadTimeout = setTimeout(function() {
            if (loading) {
                loading.classList.add('hidden');
            }
            showError('Upload timed out. Please try again.');
        }, 60000); // 60 seconds timeout
        
        // Send the file to the server
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);
        
        xhr.onload = function() {
            clearTimeout(uploadTimeout);
            if (loading) {
                loading.classList.add('hidden');
            }
            
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    
                    if (data.success) {
                        // Check if we should redirect to review page
                        if (data.redirect) {
                            window.location.href = data.redirect;
                            return;
                        }
                        
                        // Otherwise show success message with download link
                        if (result) {
                            result.classList.remove('hidden');
                        }
                        if (successMessage) {
                            successMessage.classList.remove('hidden');
                        }
                        if (errorMessage) {
                            errorMessage.classList.add('hidden');
                        }
                        
                        if (downloadLink) {
                            downloadLink.href = '/download/' + encodeURIComponent(data.filename);
                        }
                        
                        if (reviewLink) {
                            reviewLink.href = '/review/' + encodeURIComponent(data.filename);
                        }
                    } else {
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
                            errorText.textContent = data.message || 'An error occurred during processing.';
                        }
                    }
                } catch (e) {
                    showError('Error parsing server response.');
                    console.error('Error parsing response:', e);
                }
            } else {
                showError('Server error: ' + xhr.status);
                console.error('Server error:', xhr.status);
            }
        };
        
        xhr.onerror = function() {
            clearTimeout(uploadTimeout);
            if (loading) {
                loading.classList.add('hidden');
            }
            showError('Network error. Please try again.');
            console.error('Network error');
        };
        
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
    
    // REVIEW PAGE FUNCTIONALITY
    
    // Get all interactive elements
    const commentButtons = document.querySelectorAll('.comment-btn');
    const tagButtons = document.querySelectorAll('.tag-btn');
    const copyButtons = document.querySelectorAll('.copy-btn');
    const resetButtons = document.querySelectorAll('.reset-btn');
    const compileButton = document.getElementById('compile-btn');
    const compiledContainer = document.getElementById('compiled-feedback-container');
    const compiledTextarea = document.getElementById('compiled-feedback');
    const copyCompiledButton = document.getElementById('copy-compiled-btn');
    const downloadFeedbackButton = document.getElementById('download-feedback-btn');
    const closeCompiledButton = document.getElementById('close-compiled-btn');
    const saveFeedbackButton = document.getElementById('save-feedback-btn');
    const successToast = document.getElementById('success-toast');
    
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
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                const comment = this.getAttribute('data-comment');
                insertComment(id, comment);
            });
        });
    }
    
    // Handle tag button clicks
    if (tagButtons) {
        tagButtons.forEach(button => {
            button.addEventListener('click', function() {
                const id = this.closest('.question-card').getAttribute('data-id');
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
        
        // Focus the textarea
        textarea.focus();
    }
    
    // Handle copy button clicks
    if (copyButtons) {
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                const textarea = document.getElementById(`feedback-${id}`);
                if (textarea) {
                    copyToClipboard(textarea.value);
                    showToast('Feedback copied to clipboard!');
                }
            });
        });
    }
    
    // Handle reset button clicks
    if (resetButtons) {
        resetButtons.forEach(button => {
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                const textarea = document.getElementById(`feedback-${id}`);
                
                if (textarea && originalTemplates[id]) {
                    textarea.value = originalTemplates[id];
                }
            });
        });
    }
    
    // Handle compile button click
    if (compileButton) {
        compileButton.addEventListener('click', function() {
            compileAllFeedback();
        });
    }
    
    // Handle copy compiled button click
    if (copyCompiledButton) {
        copyCompiledButton.addEventListener('click', function() {
            if (compiledTextarea) {
                copyToClipboard(compiledTextarea.value);
                showToast('All feedback copied to clipboard!');
            }
        });
    }
    
    // Handle download feedback button click
    if (downloadFeedbackButton) {
        downloadFeedbackButton.addEventListener('click', function() {
            if (compiledTextarea && compiledTextarea.value) {
                downloadFeedback(compiledTextarea.value);
            }
        });
    }
    
    // Handle close compiled button click
    if (closeCompiledButton) {
        closeCompiledButton.addEventListener('click', function() {
            if (compiledContainer) {
                compiledContainer.classList.add('hidden');
            }
        });
    }
    
    // Handle save feedback button click
    if (saveFeedbackButton) {
        saveFeedbackButton.addEventListener('click', function() {
            const feedbackText = compileAllFeedback(false);
            saveFeedbackToServer(feedbackText);
        });
    }
    
    // Compile all feedback
    function compileAllFeedback(showCompiled = true) {
        let allFeedback = '';
        
        document.querySelectorAll('.question-card').forEach(card => {
            const id = card.getAttribute('data-id');
            const titleElement = card.querySelector('.question-title');
            const title = titleElement ? titleElement.textContent : `Section ${id}`;
            const textarea = document.getElementById(`feedback-${id}`);
            
            if (textarea && textarea.value.trim()) {
                allFeedback += `## ${title} ##\n\n${textarea.value.trim()}\n\n`;
            }
        });
        
        if (compiledTextarea) {
            compiledTextarea.value = allFeedback;
        }
        
        if (showCompiled && compiledContainer) {
            compiledContainer.classList.remove('hidden');
        }
        
        return allFeedback;
    }
    
    // Save feedback to server
    function saveFeedbackToServer(feedbackText) {
        if (!feedbackText || !dmpFilename) {
            showToast('No feedback to save!', 'error');
            return;
        }
        
        const data = {
            filename: dmpFilename,
            feedback: feedbackText
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
        a.download = `DMP_Feedback_${new Date().toISOString().slice(0,10)}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
    
    // Copy text to clipboard
    function copyToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
    
    // Show toast message
    function showToast(message, type = 'success') {
        const toast = document.getElementById('success-toast');
        if (!toast) return;
        
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
    
    // TEMPLATE EDITOR FUNCTIONALITY
    
    // Get template editor elements
    const saveTemplateButtons = document.querySelectorAll('.save-template-btn');
    const saveAllTemplatesButton = document.getElementById('save-all-templates');
    
    // Handle individual save buttons
    if (saveTemplateButtons) {
        saveTemplateButtons.forEach(button => {
            button.addEventListener('click', function() {
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
        saveAllTemplatesButton.addEventListener('click', function() {
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
});