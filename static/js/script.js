document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file-btn');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const uploadBtn = document.getElementById('upload-btn');
    const clearBtn = document.getElementById('clear-btn');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const downloadLink = document.getElementById('download-link');
    const newUploadBtn = document.getElementById('new-upload-btn');
    const tryAgainBtn = document.getElementById('try-again-btn');
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    // Highlight drop area when dragging file over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFiles(files);
        }
    }
    
    // Handle selected files
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFiles(fileInput.files);
        }
    });
    
    function handleFiles(files) {
        const file = files[0];
        
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
        fileName.textContent = file.name;
        fileInfo.classList.remove('hidden');
    }
    
    // Handle upload button
    uploadBtn.addEventListener('click', () => {
        if (fileInput.files.length === 0) {
            showError('Please select a file first.');
            return;
        }
        
        const file = fileInput.files[0];
        
        // Validate file again before upload
        if (file.type !== 'application/pdf') {
            showError('Please select a PDF file.');
            return;
        }
        
        uploadFile(file);
    });
    
    // Handle clear button
    clearBtn.addEventListener('click', () => {
        resetForm();
    });
    
    // Handle new upload button
    newUploadBtn.addEventListener('click', () => {
        resetForm();
        result.classList.add('hidden');
        fileInfo.classList.add('hidden');
    });
    
    // Handle try again button
    tryAgainBtn.addEventListener('click', () => {
        resetForm();
        result.classList.add('hidden');
    });
    
    function resetForm() {
        fileInput.value = '';
        fileName.textContent = '';
        fileInfo.classList.add('hidden');
    }
    
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Show loading spinner
        fileInfo.classList.add('hidden');
        loading.classList.remove('hidden');
        
        // Set up upload timeout
        const uploadTimeout = setTimeout(() => {
            loading.classList.add('hidden');
            showError('Upload timed out. Please try again.');
        }, 60000); // 60 seconds timeout
        
        // Send the file to the server
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            clearTimeout(uploadTimeout);
            if (!response.ok) {
                throw new Error(`Server error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            loading.classList.add('hidden');
            result.classList.remove('hidden');
            
            if (data.success) {
                successMessage.classList.remove('hidden');
                errorMessage.classList.add('hidden');
                downloadLink.href = `/download/${encodeURIComponent(data.filename)}`;
            } else {
                successMessage.classList.add('hidden');
                errorMessage.classList.remove('hidden');
                errorText.textContent = data.message || 'An error occurred during processing.';
            }
        })
        .catch(error => {
            clearTimeout(uploadTimeout);
            loading.classList.add('hidden');
            result.classList.remove('hidden');
            successMessage.classList.add('hidden');
            errorMessage.classList.remove('hidden');
            errorText.textContent = 'An error occurred during upload. Please try again.';
            console.error('Error:', error);
        });
    }
    
    function showError(message) {
        result.classList.remove('hidden');
        successMessage.classList.add('hidden');
        errorMessage.classList.remove('hidden');
        errorText.textContent = message;
    }
});