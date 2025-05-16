// static/js/template_editor.js

document.addEventListener('DOMContentLoaded', function() {
    // Tab navigation
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons and panels
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanels.forEach(panel => panel.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Show corresponding panel
            const tabId = this.getAttribute('data-tab');
            document.getElementById(`${tabId}-panel`).classList.add('active');
        });
    });
    
    // TEMPLATES TAB FUNCTIONALITY
    const saveTemplateButtons = document.querySelectorAll('.save-template-btn');
    const saveAllTemplatesButton = document.getElementById('save-all-templates');
    
    // Handle individual template save buttons
    if (saveTemplateButtons) {
        saveTemplateButtons.forEach(button => {
            button.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                const templateText = document.getElementById(`template-${id}`).value;
                
                const data = {};
                data[id] = templateText;
                
                saveToServer('/save_templates', data);
            });
        });
    }
    
    // Handle save all templates button
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
            
            saveToServer('/save_templates', templates);
        });
    }
    
    // COMMENTS TAB FUNCTIONALITY
    const addCommentBtn = document.getElementById('add-comment-btn');
    const commentsContainer = document.getElementById('comments-container');
    const saveCommentsBtn = document.getElementById('save-comments-btn');
    
    // Add new comment
    if (addCommentBtn) {
        addCommentBtn.addEventListener('click', function() {
            const newCommentId = 'new_comment_' + Date.now();
            
            const newComment = document.createElement('div');
            newComment.className = 'edit-item';
            newComment.setAttribute('data-id', newCommentId);
            newComment.innerHTML = `
                <div class="edit-header">
                    <input type="text" class="key-input" value="" placeholder="Comment key">
                    <button class="delete-btn" data-type="comment" data-id="${newCommentId}">Delete</button>
                </div>
                <textarea class="content-input"></textarea>
            `;
            
            commentsContainer.appendChild(newComment);
            
            // Add event listener for delete button
            newComment.querySelector('.delete-btn').addEventListener('click', handleDelete);
        });
    }
    
    // Save all comments
    if (saveCommentsBtn) {
        saveCommentsBtn.addEventListener('click', function() {
            const comments = {};
            
            document.querySelectorAll('#comments-container .edit-item').forEach(item => {
                const keyInput = item.querySelector('.key-input');
                const contentInput = item.querySelector('.content-input');
                
                // Skip items with empty keys
                if (keyInput.value.trim() !== '') {
                    comments[keyInput.value.trim()] = contentInput.value;
                }
            });
            
            saveToServer('/save_comments', comments);
        });
    }
    
    // KEYWORDS TAB FUNCTIONALITY
    const addKeywordGroupBtn = document.getElementById('add-keyword-group-btn');
    const keywordsContainer = document.getElementById('keywords-container');
    const saveKeywordsBtn = document.getElementById('save-keywords-btn');
    
    // Add new keyword group
    if (addKeywordGroupBtn) {
        addKeywordGroupBtn.addEventListener('click', function() {
            const newGroupId = 'new_group_' + Date.now();
            
            const newGroup = document.createElement('div');
            newGroup.className = 'edit-item';
            newGroup.setAttribute('data-id', newGroupId);
            newGroup.innerHTML = `
                <div class="edit-header">
                    <input type="text" class="key-input" value="" placeholder="Category name">
                    <button class="delete-btn" data-type="keyword" data-id="${newGroupId}">Delete</button>
                </div>
                <div class="phrases-container">
                    <div class="phrase-item">
                        <input type="text" class="phrase-input" value="">
                        <button class="remove-phrase-btn">Remove</button>
                    </div>
                    <button class="add-phrase-btn">Add Phrase</button>
                </div>
            `;
            
            keywordsContainer.appendChild(newGroup);
            
            // Add event listeners
            newGroup.querySelector('.delete-btn').addEventListener('click', handleDelete);
            newGroup.querySelector('.add-phrase-btn').addEventListener('click', handleAddPhrase);
            newGroup.querySelector('.remove-phrase-btn').addEventListener('click', handleRemovePhrase);
        });
    }
    
    // Add phrase to a group
    function handleAddPhrase() {
        const phrasesContainer = this.closest('.phrases-container');
        
        const newPhrase = document.createElement('div');
        newPhrase.className = 'phrase-item';
        newPhrase.innerHTML = `
            <input type="text" class="phrase-input" value="">
            <button class="remove-phrase-btn">Remove</button>
        `;
        
        phrasesContainer.insertBefore(newPhrase, this);
        
        // Add event listener for remove button
        newPhrase.querySelector('.remove-phrase-btn').addEventListener('click', handleRemovePhrase);
    }
    
    // Remove phrase from a group
    function handleRemovePhrase() {
        const phraseItem = this.closest('.phrase-item');
        const phrasesContainer = phraseItem.closest('.phrases-container');
        
        // Don't remove if it's the last phrase
        if (phrasesContainer.querySelectorAll('.phrase-item').length > 1) {
            phraseItem.remove();
        }
    }
    
    // Save all keywords
    if (saveKeywordsBtn) {
        saveKeywordsBtn.addEventListener('click', function() {
            const keywords = {};
            
            document.querySelectorAll('#keywords-container .edit-item').forEach(item => {
                const keyInput = item.querySelector('.key-input');
                const phraseInputs = item.querySelectorAll('.phrase-input');
                
                // Skip items with empty keys
                if (keyInput.value.trim() !== '') {
                    const phrases = [];
                    
                    phraseInputs.forEach(input => {
                        if (input.value.trim() !== '') {
                            phrases.push(input.value.trim());
                        }
                    });
                    
                    keywords[keyInput.value.trim()] = phrases;
                }
            });
            
            saveToServer('/save_key_phrases', keywords);
        });
    }
    
    // STRUCTURE TAB FUNCTIONALITY
    const addSectionBtn = document.getElementById('add-section-btn');
    const structureContainer = document.getElementById('structure-container');
    const saveStructureBtn = document.getElementById('save-structure-btn');
    
    // Add new section
    if (addSectionBtn) {
        addSectionBtn.addEventListener('click', function() {
            const newSectionId = 'new_section_' + Date.now();
            
            const newSection = document.createElement('div');
            newSection.className = 'section-item';
            newSection.setAttribute('data-section', newSectionId);
            newSection.innerHTML = `
                <div class="section-header">
                    <input type="text" class="section-input" value="" placeholder="Section title">
                    <button class="delete-btn" data-type="section" data-id="${newSectionId}">Delete Section</button>
                </div>
                <div class="questions-container">
                    <div class="question-item">
                        <input type="text" class="question-input" value="">
                        <button class="remove-question-btn">Remove</button>
                    </div>
                    <button class="add-question-btn">Add Question</button>
                </div>
            `;
            
            structureContainer.appendChild(newSection);
            
            // Add event listeners
            newSection.querySelector('.delete-btn').addEventListener('click', handleDelete);
            newSection.querySelector('.add-question-btn').addEventListener('click', handleAddQuestion);
            newSection.querySelector('.remove-question-btn').addEventListener('click', handleRemoveQuestion);
        });
    }
    
    // Add question to a section
    function handleAddQuestion() {
        const questionsContainer = this.closest('.questions-container');
        
        const newQuestion = document.createElement('div');
        newQuestion.className = 'question-item';
        newQuestion.innerHTML = `
            <input type="text" class="question-input" value="">
            <button class="remove-question-btn">Remove</button>
        `;
        
        questionsContainer.insertBefore(newQuestion, this);
        
        // Add event listener for remove button
        newQuestion.querySelector('.remove-question-btn').addEventListener('click', handleRemoveQuestion);
    }
    
    // Remove question from a section
    function handleRemoveQuestion() {
        const questionItem = this.closest('.question-item');
        const questionsContainer = questionItem.closest('.questions-container');
        
        // Don't remove if it's the last question
        if (questionsContainer.querySelectorAll('.question-item').length > 1) {
            questionItem.remove();
        }
    }
    
    // Save structure
    if (saveStructureBtn) {
        saveStructureBtn.addEventListener('click', function() {
            const structure = {};
            
            document.querySelectorAll('#structure-container .section-item').forEach(item => {
                const sectionInput = item.querySelector('.section-input');
                const questionInputs = item.querySelectorAll('.question-input');
                
                // Skip items with empty section titles
                if (sectionInput.value.trim() !== '') {
                    const questions = [];
                    
                    questionInputs.forEach(input => {
                        if (input.value.trim() !== '') {
                            questions.push(input.value.trim());
                        }
                    });
                    
                    // Only add if there's at least one question
                    if (questions.length > 0) {
                        structure[sectionInput.value.trim()] = questions;
                    }
                }
            });
            
            saveToServer('/save_dmp_structure', structure);
        });
    }
    
    // COMMON FUNCTIONALITY
    
    // Handle delete button clicks
    function handleDelete() {
        const type = this.getAttribute('data-type');
        const id = this.getAttribute('data-id');
        
        if (type === 'comment') {
            const commentItem = document.querySelector(`.edit-item[data-id="${id}"]`);
            if (commentItem) {
                commentItem.remove();
            }
        } else if (type === 'keyword') {
            const keywordItem = document.querySelector(`.edit-item[data-id="${id}"]`);
            if (keywordItem) {
                keywordItem.remove();
            }
        } else if (type === 'section') {
            const sectionItem = document.querySelector(`.section-item[data-section="${id}"]`);
            if (sectionItem) {
                sectionItem.remove();
            }
        }
    }
    
    // Add event listeners to existing elements
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', handleDelete);
    });
    
    document.querySelectorAll('.add-phrase-btn').forEach(button => {
        button.addEventListener('click', handleAddPhrase);
    });
    
    document.querySelectorAll('.remove-phrase-btn').forEach(button => {
        button.addEventListener('click', handleRemovePhrase);
    });
    
    document.querySelectorAll('.add-question-btn').forEach(button => {
        button.addEventListener('click', handleAddQuestion);
    });
    
    document.querySelectorAll('.remove-question-btn').forEach(button => {
        button.addEventListener('click', handleRemoveQuestion);
    });
    
    // Save to server
    function saveToServer(endpoint, data) {
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Saved successfully!');
            } else {
                showToast(`Error: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            showToast(`Error: ${error.message}`, 'error');
        });
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
});