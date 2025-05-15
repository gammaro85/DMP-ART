// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
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
    
    // Review page script
    var copyButtons = document.querySelectorAll('.copy-btn');
    var emailButtons = document.querySelectorAll('.email-btn');
    var saveTemplatesBtn = document.getElementById('save-templates');
    var successToast = document.getElementById('success-toast');
    
    // Handle copy button clicks
    if (copyButtons) {
        copyButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                var id = this.getAttribute('data-id');
                var textarea = document.getElementById('template-' + id);
                if (textarea) {
                    copyToClipboard(textarea.value);
                    alert('Text copied to clipboard!');
                }
            });
        });
    }
    
    // Handle email button clicks
    if (emailButtons) {
        emailButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                var id = this.getAttribute('data-id');
                var textarea = document.getElementById('template-' + id);
                var questionEl = document.querySelector('.question-card[data-id="' + id + '"] .question-title');
                
                if (textarea && questionEl) {
                    // Create email with subject and body
                    var subject = encodeURIComponent('DMP Feedback: ' + questionEl.textContent);
                    var body = encodeURIComponent(textarea.value);
                    window.location.href = 'mailto:?subject=' + subject + '&body=' + body;
                }
            });
        });
    }
    
    // Handle save all templates
    if (saveTemplatesBtn) {
        saveTemplatesBtn.addEventListener('click', function() {
            var templates = {};
            
            document.querySelectorAll('.question-card').forEach(function(card) {
                var id = card.getAttribute('data-id');
                var textarea = document.getElementById('template-' + id);
                if (textarea) {
                    templates[id] = textarea.value;
                }
            });
            
            // Send templates to server using XMLHttpRequest
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/save_templates', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            
            xhr.onload = function() {
                if (xhr.status === 200) {
                    try {
                        var data = JSON.parse(xhr.responseText);
                        if (data.success) {
                            showToast();
                        } else {
                            alert('Error: ' + data.message);
                        }
                    } catch (e) {
                        alert('Error parsing server response.');
                    }
                } else {
                    alert('Server error: ' + xhr.status);
                }
            };
            
            xhr.onerror = function() {
                alert('Network error. Please try again.');
            };
            
            xhr.send(JSON.stringify(templates));
        });
    }
    
    // Function to copy text to clipboard
    function copyToClipboard(text) {
        var textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
    
    // Function to show success toast
    function showToast() {
        if (successToast) {
            successToast.classList.add('show');
            
            setTimeout(function() {
                successToast.classList.remove('show');
            }, 3000);
        }
    }
    
    // Template editor script
    var saveTemplateButtons = document.querySelectorAll('.save-template-btn');
    var saveAllTemplatesButton = document.getElementById('save-all-templates');
    
    // Handle individual save buttons
    if (saveTemplateButtons) {
        saveTemplateButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                var id = this.getAttribute('data-id');
                var templateInput = document.getElementById('template-' + id);
                
                if (templateInput) {
                    saveTemplate(id, templateInput.value);
                }
            });
        });
    }
    
    // Handle save all button
    if (saveAllTemplatesButton) {
        saveAllTemplatesButton.addEventListener('click', function() {
            var templates = {};
            
            document.querySelectorAll('.template-item').forEach(function(item) {
                var id = item.getAttribute('data-id');
                var templateInput = document.getElementById('template-' + id);
                
                if (templateInput) {
                    templates[id] = templateInput.value;
                }
            });
            
            saveAllTemplates(templates);
        });
    }
    
    // Function to save a single template
    function saveTemplate(id, text) {
        var data = {};
        data[id] = text;
        
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/save_templates', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onload = function() {
            if (xhr.status === 200) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        showToast();
                    } else {
                        alert('Error: ' + response.message);
                    }
                } catch (e) {
                    alert('Error parsing server response.');
                }
            } else {
                alert('Server error: ' + xhr.status);
            }
        };
        
        xhr.onerror = function() {
            alert('Network error. Please try again.');
        };
        
        xhr.send(JSON.stringify(data));
    }
    
    // Function to save all templates
    function saveAllTemplates(templates) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/save_templates', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        
        xhr.onload = function() {
            if (xhr.status === 200) {
                try {
                    var response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        showToast();
                    } else {
                        alert('Error: ' + response.message);
                    }
                } catch (e) {
                    alert('Error parsing server response.');
                }
            } else {
                alert('Server error: ' + xhr.status);
            }
        };
        
        xhr.onerror = function() {
            alert('Network error. Please try again.');
        };
        
        xhr.send(JSON.stringify(templates));
    }
});