// Template Editor JavaScript - Enhanced and Consolidated
(function () {
    'use strict';

    // Global state for dynamic categories
    let availableCategories = [];

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function () {
        initializeTemplateEditor();
    });

    async function initializeTemplateEditor() {
        console.log('Initializing template editor...');

        // Load categories dynamically first
        await loadDynamicCategories();

        // Initialize all tabs
        initializeTabSwitching();
        initializeTemplatesTab();
        initializeCommentsTab();
        initializeKeywordsTab();
        initializeStructureTab();

        console.log('Template editor initialized successfully');
    }

    // DYNAMIC CATEGORY LOADING
    async function loadDynamicCategories() {
        try {
            const response = await fetch('/api/discover-categories');
            const data = await response.json();

            if (data.success) {
                availableCategories = data.categories;
                renderCategoryTabs();
                console.log(`Loaded ${data.count} categories dynamically`);
            } else {
                console.error('Failed to load categories:', data.message);
                showNotification('Failed to load categories', 'error');
            }
        } catch (error) {
            console.error('Error discovering categories:', error);
            showNotification('Error loading categories', 'error');
        }
    }

    function renderCategoryTabs() {
        const tabNav = document.getElementById('tab-navigation');
        const tabContent = document.getElementById('tab-content');

        if (!tabNav || !tabContent) {
            console.error('Tab navigation or content element not found');
            return;
        }

        // Find add button (we'll re-add it at the end)
        const addBtn = tabNav.querySelector('.add-category-btn');

        // Remove existing dynamic category tabs
        const existingTabs = tabNav.querySelectorAll('[data-tab]');
        existingTabs.forEach(tab => {
            const tabType = tab.getAttribute('data-tab');
            if (tabType !== 'dmp-structure' && tabType !== 'quick-comments') {
                tab.remove();
            }
        });

        // Remove existing dynamic category panels
        const existingPanels = tabContent.querySelectorAll('[id$="-panel"]');
        existingPanels.forEach(panel => {
            const panelId = panel.id;
            if (!panelId.includes('dmp-structure') && !panelId.includes('quick-comments')) {
                panel.remove();
            }
        });

        // Add dynamic category tabs
        availableCategories.forEach(category => {
            // Create tab button
            const btn = document.createElement('button');
            btn.className = 'tab-btn';
            btn.setAttribute('data-tab', category.id);
            btn.innerHTML = `
                <i class="fas fa-tags"></i>
                ${category.display_name}
                <button class="delete-category-btn" onclick="event.stopPropagation(); deleteCategoryConfirm('${category.id}')" title="Delete category">
                    <i class="fas fa-times"></i>
                </button>
            `;

            // Insert before add button
            if (addBtn) {
                tabNav.insertBefore(btn, addBtn);
            } else {
                tabNav.appendChild(btn);
            }

            // Create tab panel
            const panel = document.createElement('div');
            panel.className = 'tab-panel';
            panel.id = `${category.id}-panel`;
            panel.innerHTML = `
                <div class="panel-header">
                    <h2>${category.display_name}</h2>
                    <p>Edit feedback templates for the ${category.display_name} category.</p>
                </div>
                <div class="category-content" id="${category.id}-content">
                    Loading...
                </div>
            `;

            tabContent.appendChild(panel);
        });

        // Re-attach click handlers after rendering
        attachTabClickHandlers();
    }

    function attachTabClickHandlers() {
        const tabs = document.querySelectorAll('.tab-btn');

        tabs.forEach(tab => {
            // Remove existing listeners by cloning
            const newTab = tab.cloneNode(true);
            tab.parentNode.replaceChild(newTab, tab);

            newTab.addEventListener('click', function(e) {
                // Don't trigger if clicking delete button
                if (e.target.closest('.delete-category-btn')) {
                    return;
                }

                const targetTab = this.getAttribute('data-tab');

                // Remove active class from all tabs and panels
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

                // Add active class to clicked tab
                this.classList.add('active');

                // Show corresponding panel
                const targetPanel = document.getElementById(`${targetTab}-panel`);
                if (targetPanel) {
                    targetPanel.classList.add('active');

                    // Load category content if it's a dynamic category
                    if (targetTab !== 'dmp-structure' && targetTab !== 'quick-comments') {
                        loadCategoryContent(targetTab);
                    }
                }
            });
        });

        // Add click handler for "Create Category" button
        const addBtn = document.getElementById('add-category-btn');
        if (addBtn) {
            addBtn.onclick = createNewCategory;
        }
    }

    async function loadCategoryContent(categoryId) {
        const contentDiv = document.getElementById(`${categoryId}-content`);
        if (!contentDiv) return;

        try {
            const response = await fetch(`/config/${categoryId}.json`);
            const data = await response.json();

            // Render category content here
            contentDiv.innerHTML = '<p>Category content loaded (feature in development)</p>';
            // TODO: Render editable sections based on data
        } catch (error) {
            console.error(`Error loading category ${categoryId}:`, error);
            contentDiv.innerHTML = '<p class="error">Error loading category content</p>';
        }
    }

    function createNewCategory() {
        showCategoryModal();
    }

    // Modal dialog for creating a new category
    function showCategoryModal() {
        // Create modal elements
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'modal-overlay';
        modalOverlay.style.position = 'fixed';
        modalOverlay.style.top = '0';
        modalOverlay.style.left = '0';
        modalOverlay.style.width = '100vw';
        modalOverlay.style.height = '100vh';
        modalOverlay.style.background = 'rgba(0,0,0,0.5)';
        modalOverlay.style.display = 'flex';
        modalOverlay.style.alignItems = 'center';
        modalOverlay.style.justifyContent = 'center';
        modalOverlay.style.zIndex = '9999';

        const modal = document.createElement('div');
        modal.className = 'modal-dialog';
        modal.style.background = '#fff';
        modal.style.padding = '2em';
        modal.style.borderRadius = '8px';
        modal.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
        modal.style.minWidth = '320px';
        modal.style.maxWidth = '90vw';

        modal.innerHTML = `
            <h2>Create New Category</h2>
            <label for="categoryNameInput">Category name (lowercase, no spaces):</label>
            <input type="text" id="categoryNameInput" style="width:100%;margin-bottom:1em;" autocomplete="off" />
            <div id="categoryModalError" style="color:red;min-height:1.5em;margin-bottom:1em;"></div>
            <div style="text-align:right;">
                <button id="categoryModalCancel" style="margin-right:1em;">Cancel</button>
                <button id="categoryModalCreate">Create</button>
            </div>
        `;

        modalOverlay.appendChild(modal);
        document.body.appendChild(modalOverlay);

        const input = modal.querySelector('#categoryNameInput');
        const errorDiv = modal.querySelector('#categoryModalError');
        const btnCancel = modal.querySelector('#categoryModalCancel');
        const btnCreate = modal.querySelector('#categoryModalCreate');

        // Focus input
        input.focus();

        // Remove modal helper
        function closeModal() {
            document.body.removeChild(modalOverlay);
        }

        // Cancel button
        btnCancel.addEventListener('click', function() {
            closeModal();
        });

        // Create button
        btnCreate.addEventListener('click', function() {
            const categoryName = input.value.trim();
            // Validate category name
            if (!categoryName) {
                errorDiv.textContent = 'Category name is required.';
                input.focus();
                return;
            }
            if (!/^[a-z0-9_]+$/.test(categoryName)) {
                errorDiv.textContent = 'Category name must be lowercase alphanumeric with underscores only.';
                input.focus();
                return;
            }
            if (availableCategories.some(c => c.id === categoryName)) {
                errorDiv.textContent = 'Category already exists.';
                input.focus();
                return;
            }

            // Create empty category file
            const emptyCategory = {
                "_category_name": categoryName,
                "1.1": {},
                "1.2": {},
                "2.1": {},
                "2.2": {},
                "3.1": {},
                "3.2": {},
                "4.1": {},
                "4.2": {},
                "5.1": {},
                "5.2": {},
                "5.3": {},
                "5.4": {},
                "6.1": {},
                "6.2": {}
            };

            // Save new category (you'll need a backend endpoint for this)
            fetch(`/api/create-category`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: categoryName, content: emptyCategory })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Category created successfully', 'success');
                    loadDynamicCategories(); // Reload categories
                    closeModal();
                } else {
                    errorDiv.textContent = data.message || 'Failed to create category';
                }
            })
            .catch(error => {
                console.error('Error creating category:', error);
                errorDiv.textContent = 'Error creating category';
            });
        });

        // Allow Enter key to submit
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                btnCreate.click();
            }
        });
    }

    function deleteCategoryConfirm(categoryId) {
        if (!confirm(`Are you sure you want to delete the "${categoryId}" category? This cannot be undone.`)) {
            return;
        }

        fetch(`/api/delete-category/${categoryId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Category deleted successfully', 'success');
                loadDynamicCategories(); // Reload categories
            } else {
                showNotification(data.message || 'Failed to delete category', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting category:', error);
            showNotification('Error deleting category', 'error');
        });
    }

    // Make deleteCategoryConfirm available globally for onclick handler
    window.deleteCategoryConfirm = deleteCategoryConfirm;

    function showNotification(message, type = 'info') {
        // Simple notification - can be enhanced with toast library
        console.log(`[${type.toUpperCase()}] ${message}`);
        alert(message);
    }

    // TAB SWITCHING FUNCTIONALITY
    function initializeTabSwitching() {
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

    // TEMPLATES TAB FUNCTIONALITY
    function initializeTemplatesTab() {
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

    function saveIndividualTemplate(id, content) {
        const data = {};
        data[id] = content;

        saveToServer('/save_templates', data);
    }

    function saveAllTemplates() {
        const templates = {};

        document.querySelectorAll('.template-input').forEach(textarea => {
            const id = textarea.id.replace('template-', '');
            templates[id] = textarea.value;
        });

        saveToServer('/save_templates', templates);
    }

    // COMMENTS TAB FUNCTIONALITY
    function initializeCommentsTab() {
        const addCommentBtn = document.getElementById('add-comment-btn');
        const commentsContainer = document.getElementById('comments-container');
        const saveCommentsBtn = document.getElementById('save-comments-btn');

        // Add new comment
        if (addCommentBtn) {
            addCommentBtn.addEventListener('click', function () {
                const newCommentId = 'new_comment_' + Date.now();

                const newComment = document.createElement('div');
                newComment.className = 'edit-item';
                newComment.setAttribute('data-id', newCommentId);
                newComment.innerHTML = `
                    <div class="edit-header">
                        <input type="text" class="key-input" value="" placeholder="Comment key">
                        <button class="delete-btn" data-type="comment" data-id="${newCommentId}">Delete</button>
                    </div>
                    <textarea class="content-input" placeholder="Comment text"></textarea>
                `;

                commentsContainer.appendChild(newComment);

                // Add event listener to the new delete button
                newComment.querySelector('.delete-btn').addEventListener('click', handleDelete);
            });
        }

        // Save comments
        if (saveCommentsBtn) {
            saveCommentsBtn.addEventListener('click', function () {
                const comments = {};

                document.querySelectorAll('#comments-container .edit-item').forEach(item => {
                    const keyInput = item.querySelector('.key-input');
                    const contentInput = item.querySelector('.content-input');

                    if (keyInput.value.trim() !== '') {
                        comments[keyInput.value.trim()] = contentInput.value;
                    }
                });

                saveToServer('/save_comments', comments);
            });
        }
    }

    // KEYWORDS TAB FUNCTIONALITY
    function initializeKeywordsTab() {
        const addKeywordBtn = document.getElementById('add-keyword-btn');
        const keywordsContainer = document.getElementById('keywords-container');
        const saveKeywordsBtn = document.getElementById('save-keywords-btn');

        // Add new keyword
        if (addKeywordBtn) {
            addKeywordBtn.addEventListener('click', function () {
                const newKeywordId = 'new_keyword_' + Date.now();

                const newKeyword = document.createElement('div');
                newKeyword.className = 'edit-item';
                newKeyword.setAttribute('data-id', newKeywordId);
                newKeyword.innerHTML = `
                    <div class="edit-header">
                        <input type="text" class="key-input" value="" placeholder="Keyword">
                        <button class="delete-btn" data-type="keyword" data-id="${newKeywordId}">Delete</button>
                    </div>
                    <div class="phrases-container">
                        <div class="phrase-item">
                            <input type="text" class="phrase-input" value="" placeholder="Phrase">
                            <button class="remove-phrase-btn">Remove</button>
                        </div>
                        <button class="add-phrase-btn">Add Phrase</button>
                    </div>
                `;

                keywordsContainer.appendChild(newKeyword);

                // Add event listeners to new elements
                newKeyword.querySelector('.delete-btn').addEventListener('click', handleDelete);
                newKeyword.querySelector('.add-phrase-btn').addEventListener('click', handleAddPhrase);
                newKeyword.querySelector('.remove-phrase-btn').addEventListener('click', handleRemovePhrase);
            });
        }

        // Save keywords
        if (saveKeywordsBtn) {
            saveKeywordsBtn.addEventListener('click', function () {
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
    }

    // Phrase management functions
    function handleAddPhrase() {
        const phrasesContainer = this.parentNode;
        const newPhrase = document.createElement('div');
        newPhrase.className = 'phrase-item';
        newPhrase.innerHTML = `
            <input type="text" class="phrase-input" value="" placeholder="Phrase">
            <button class="remove-phrase-btn">Remove</button>
        `;

        // Insert before the "Add Phrase" button
        phrasesContainer.insertBefore(newPhrase, this);

        // Add event listener to the new remove button
        newPhrase.querySelector('.remove-phrase-btn').addEventListener('click', handleRemovePhrase);
    }

    function handleRemovePhrase() {
        const phraseItem = this.parentNode;
        const phrasesContainer = phraseItem.parentNode;

        // Don't remove if it's the only phrase item
        const phraseItems = phrasesContainer.querySelectorAll('.phrase-item');
        if (phraseItems.length > 1) {
            phraseItem.remove();
        } else {
            // Clear the input instead
            const phraseInput = phraseItem.querySelector('.phrase-input');
            if (phraseInput) {
                phraseInput.value = '';
            }
        }
    }

    // STRUCTURE TAB FUNCTIONALITY
    function initializeStructureTab() {
        const addSectionBtn = document.getElementById('add-section-btn');
        const structureContainer = document.getElementById('structure-container');
        const saveStructureBtn = document.getElementById('save-structure-btn');

        // Add new section
        if (addSectionBtn) {
            addSectionBtn.addEventListener('click', function () {
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

                // Add event listeners to new elements
                newSection.querySelector('.delete-btn').addEventListener('click', handleDelete);
                newSection.querySelector('.add-question-btn').addEventListener('click', handleAddQuestion);
                newSection.querySelector('.remove-question-btn').addEventListener('click', handleRemoveQuestion);
            });
        }

        // Save structure
        if (saveStructureBtn) {
            saveStructureBtn.addEventListener('click', function () {
                const structure = {};

                document.querySelectorAll('#structure-container .section-item').forEach(item => {
                    const sectionInput = item.querySelector('.section-input');
                    const questionInputs = item.querySelectorAll('.question-input');

                    if (sectionInput.value.trim() !== '') {
                        const questions = [];

                        questionInputs.forEach(input => {
                            if (input.value.trim() !== '') {
                                questions.push(input.value.trim());
                            }
                        });

                        if (questions.length > 0) {
                            structure[sectionInput.value.trim()] = questions;
                        }
                    }
                });

                saveToServer('/save_dmp_structure', structure);
            });
        }
    }

    // Question management functions
    function handleAddQuestion() {
        const questionsContainer = this.parentNode;
        const newQuestion = document.createElement('div');
        newQuestion.className = 'question-item';
        newQuestion.innerHTML = `
            <input type="text" class="question-input" value="">
            <button class="remove-question-btn">Remove</button>
        `;

        // Insert before the "Add Question" button
        questionsContainer.insertBefore(newQuestion, this);

        // Add event listener to the new remove button
        newQuestion.querySelector('.remove-question-btn').addEventListener('click', handleRemoveQuestion);
    }

    function handleRemoveQuestion() {
        const questionItem = this.parentNode;
        const questionsContainer = questionItem.parentNode;

        // Don't remove if it's the only question item
        const questionItems = questionsContainer.querySelectorAll('.question-item');
        if (questionItems.length > 1) {
            questionItem.remove();
        } else {
            // Clear the input instead
            const questionInput = questionItem.querySelector('.question-input');
            if (questionInput) {
                questionInput.value = '';
            }
        }
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

    function updateThemeToggle(isDark) {
        const text = document.getElementById('theme-text');
        if (text) {
            text.textContent = isDark ? 'Light Mode' : 'Dark Mode';
        }
    }
})();