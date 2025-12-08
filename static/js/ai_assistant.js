/**
 * DMP ART - AI Assistant Module
 * Provides AI-powered suggestions for DMP review
 */

class AIAssistant {
    constructor() {
        this.enabled = false;
        this.suggestions = {};
        this.currentSection = null;
        this.initialized = false;
    }

    /**
     * Initialize the AI assistant
     */
    async init() {
        if (this.initialized) return;

        try {
            await this.checkStatus();
            if (this.enabled) {
                this.addAIButtons();
                this.addAIStyles();
            }
            this.initialized = true;
            console.log('AI Assistant initialized, enabled:', this.enabled);
        } catch (e) {
            console.error('AI Assistant initialization error:', e);
        }
    }

    /**
     * Check if AI module is enabled
     */
    async checkStatus() {
        try {
            const response = await fetch('/api/ai/config');
            const data = await response.json();
            this.enabled = data.config?.enabled || false;
        } catch (e) {
            console.error('AI status check failed:', e);
            this.enabled = false;
        }
    }

    /**
     * Add AI-specific CSS styles
     */
    addAIStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .ai-suggest-btn {
                background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
                color: white !important;
                border: none !important;
            }

            .ai-suggest-btn:hover {
                background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
                transform: translateY(-1px);
            }

            .ai-section-btn {
                background: var(--bg-tertiary) !important;
                color: var(--primary-color) !important;
                border: 1px solid var(--primary-color) !important;
                padding: 6px 10px !important;
                font-size: 0.9rem !important;
            }

            .ai-section-btn:hover {
                background: var(--primary-color) !important;
                color: white !important;
            }

            .ai-suggestion-panel {
                background: var(--bg-card);
                border: 2px solid var(--primary-color);
                border-radius: 8px;
                margin: 15px 0;
                overflow: hidden;
                animation: slideIn 0.3s ease;
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .ai-panel-header {
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
                padding: 10px 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .ai-panel-header .quality-score {
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.85rem;
                font-weight: 600;
            }

            .ai-panel-header .quality-score.score-good {
                background: rgba(16, 185, 129, 0.2);
                color: #10b981;
            }

            .ai-panel-header .quality-score.score-medium {
                background: rgba(245, 158, 11, 0.2);
                color: #f59e0b;
            }

            .ai-panel-header .quality-score.score-low {
                background: rgba(239, 68, 68, 0.2);
                color: #ef4444;
            }

            .close-ai-panel {
                background: transparent;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s;
            }

            .close-ai-panel:hover {
                opacity: 1;
            }

            .ai-panel-content {
                padding: 15px;
            }

            .ai-section {
                margin-bottom: 15px;
            }

            .ai-section:last-child {
                margin-bottom: 0;
            }

            .ai-section h4 {
                color: var(--text-primary);
                font-size: 0.9rem;
                margin-bottom: 8px;
            }

            .ai-section ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }

            .ai-section li {
                background: var(--bg-tertiary);
                border: 1px solid var(--border-light);
                padding: 10px 12px;
                margin-bottom: 6px;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.9rem;
                color: var(--text-primary);
            }

            .ai-section li:hover {
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
            }

            .ai-section li .insert-btn {
                background: transparent;
                border: 1px solid currentColor;
                color: inherit;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 0.75rem;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s;
            }

            .ai-section li:hover .insert-btn {
                opacity: 1;
            }

            .ai-issues {
                background: rgba(239, 68, 68, 0.05);
                border-radius: 6px;
                padding: 10px;
            }

            .ai-issues h4 {
                color: #ef4444;
            }

            .ai-issues li {
                background: transparent;
                border: none;
                padding: 5px 0;
                color: var(--text-secondary);
                cursor: default;
            }

            .ai-issues li:hover {
                background: transparent;
                color: var(--text-secondary);
            }

            .ai-loading {
                text-align: center;
                padding: 20px;
                color: var(--text-secondary);
            }

            .ai-loading i {
                font-size: 2rem;
                margin-bottom: 10px;
                color: var(--primary-color);
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Add AI buttons to the UI
     */
    addAIButtons() {
        // Add main AI button in header
        const headerActions = document.querySelector('.header-action-buttons-nav');
        if (headerActions && !document.querySelector('.ai-suggest-btn')) {
            const aiBtn = document.createElement('button');
            aiBtn.className = 'action-btn ai-suggest-btn';
            aiBtn.innerHTML = '<i class="fas fa-robot"></i> AI Sugestie';
            aiBtn.onclick = () => this.generateAllSuggestions();
            headerActions.appendChild(aiBtn);
        }

        // Add AI button to each section
        document.querySelectorAll('.question-card[data-id]').forEach(card => {
            const sectionId = card.getAttribute('data-id');
            if (!sectionId || sectionId.startsWith('_')) return;

            const feedbackActions = card.querySelector('.feedback-actions');
            if (feedbackActions && !feedbackActions.querySelector('.ai-section-btn')) {
                const sectionAiBtn = document.createElement('button');
                sectionAiBtn.className = 'btn ai-section-btn';
                sectionAiBtn.innerHTML = '<i class="fas fa-robot"></i>';
                sectionAiBtn.title = 'Sugestia AI dla tej sekcji';
                sectionAiBtn.onclick = (e) => {
                    e.preventDefault();
                    this.generateSectionSuggestion(sectionId);
                };
                feedbackActions.appendChild(sectionAiBtn);
            }
        });
    }

    /**
     * Get cache ID from URL
     */
    getCacheId() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('cache_id');
    }

    /**
     * Generate suggestions for all sections
     */
    async generateAllSuggestions() {
        const cacheId = this.getCacheId();
        if (!cacheId) {
            if (typeof showToast === 'function') {
                showToast('Brak cache_id - wgraj najpierw plik DMP', 'error');
            }
            return;
        }

        if (typeof showToast === 'function') {
            showToast('Generuję sugestie AI dla wszystkich sekcji...', 'info');
        }

        try {
            const response = await fetch('/api/ai/suggest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cache_id: cacheId })
            });

            const data = await response.json();

            if (data.success) {
                this.suggestions = data.suggestions;
                this.displayAllSuggestions();
                if (typeof showToast === 'function') {
                    showToast('Sugestie AI gotowe!', 'success');
                }
            } else {
                if (typeof showToast === 'function') {
                    showToast(data.message || 'Błąd generowania sugestii', 'error');
                }
            }
        } catch (e) {
            console.error('AI suggestion error:', e);
            if (typeof showToast === 'function') {
                showToast('Błąd połączenia z AI', 'error');
            }
        }
    }

    /**
     * Generate suggestion for a single section
     */
    async generateSectionSuggestion(sectionId) {
        const cacheId = this.getCacheId();
        if (!cacheId) {
            if (typeof showToast === 'function') {
                showToast('Brak cache_id', 'error');
            }
            return;
        }

        this.currentSection = sectionId;

        // Show loading indicator
        this.showLoadingPanel(sectionId);

        try {
            const response = await fetch('/api/ai/suggest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cache_id: cacheId,
                    section_id: sectionId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displaySectionSuggestion(sectionId, data.suggestions);
            } else {
                this.removeLoadingPanel(sectionId);
                if (typeof showToast === 'function') {
                    showToast(data.message || 'Błąd AI', 'error');
                }
            }
        } catch (e) {
            console.error('AI section suggestion error:', e);
            this.removeLoadingPanel(sectionId);
            if (typeof showToast === 'function') {
                showToast('Błąd połączenia z AI', 'error');
            }
        }
    }

    /**
     * Show loading panel while generating suggestion
     */
    showLoadingPanel(sectionId) {
        const card = document.querySelector(`[data-id="${sectionId}"]`);
        if (!card) return;

        // Remove existing panel
        const existingPanel = card.querySelector('.ai-suggestion-panel');
        if (existingPanel) existingPanel.remove();

        // Create loading panel
        const panel = document.createElement('div');
        panel.className = 'ai-suggestion-panel';
        panel.innerHTML = `
            <div class="ai-panel-header">
                <span><i class="fas fa-robot"></i> Sugestie AI</span>
                <button class="close-ai-panel" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="ai-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Analizuję treść sekcji...</p>
            </div>
        `;

        const feedbackSection = card.querySelector('.feedback-text');
        if (feedbackSection) {
            feedbackSection.parentElement.insertBefore(panel, feedbackSection);
        }
    }

    /**
     * Remove loading panel
     */
    removeLoadingPanel(sectionId) {
        const card = document.querySelector(`[data-id="${sectionId}"]`);
        if (!card) return;

        const panel = card.querySelector('.ai-suggestion-panel');
        if (panel) panel.remove();
    }

    /**
     * Display suggestions for all sections
     */
    displayAllSuggestions() {
        for (const [sectionId, suggestion] of Object.entries(this.suggestions)) {
            if (!sectionId.startsWith('_') && !suggestion.error) {
                this.displaySectionSuggestion(sectionId, suggestion);
            }
        }
    }

    /**
     * Display suggestion panel for a section
     */
    displaySectionSuggestion(sectionId, suggestion) {
        const card = document.querySelector(`[data-id="${sectionId}"]`);
        if (!card) return;

        // Remove existing panel
        const existingPanel = card.querySelector('.ai-suggestion-panel');
        if (existingPanel) existingPanel.remove();

        // Handle error
        if (suggestion.error) {
            if (typeof showToast === 'function') {
                showToast(`Błąd dla sekcji ${sectionId}: ${suggestion.error}`, 'error');
            }
            return;
        }

        // Create suggestion panel
        const panel = document.createElement('div');
        panel.className = 'ai-suggestion-panel';
        panel.innerHTML = `
            <div class="ai-panel-header">
                <span><i class="fas fa-robot"></i> Sugestie AI dla sekcji ${sectionId}</span>
                <span class="quality-score ${this.getScoreClass(suggestion.quality_score)}">
                    Jakość: ${suggestion.quality_score || 'N/A'}%
                </span>
                <button class="close-ai-panel" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="ai-panel-content">
                ${this.renderSelectedComments(sectionId, suggestion.selected_comments)}
                ${this.renderAISuggestions(sectionId, suggestion.ai_suggestions)}
                ${this.renderIssues(suggestion.issues)}
            </div>
        `;

        // Insert panel before feedback textarea
        const feedbackSection = card.querySelector('.feedback-text');
        if (feedbackSection) {
            feedbackSection.parentElement.insertBefore(panel, feedbackSection);
        }
    }

    /**
     * Render selected ready comments
     */
    renderSelectedComments(sectionId, comments) {
        if (!comments || comments.length === 0) return '';

        const items = comments.map(c => {
            const escapedComment = this.escapeHtml(c);
            return `
                <li onclick="aiAssistant.insertCommentToSection('${sectionId}', '${escapedComment}')">
                    <span>${c}</span>
                    <button class="insert-btn">+ Wstaw</button>
                </li>
            `;
        }).join('');

        return `
            <div class="ai-section">
                <h4><i class="fas fa-clipboard-list"></i> Wybrane gotowe komentarze:</h4>
                <ul>${items}</ul>
            </div>
        `;
    }

    /**
     * Render AI-generated suggestions
     */
    renderAISuggestions(sectionId, suggestions) {
        if (!suggestions || suggestions.length === 0) return '';

        const items = suggestions.map(s => {
            const escapedSuggestion = this.escapeHtml(s);
            return `
                <li onclick="aiAssistant.insertCommentToSection('${sectionId}', '${escapedSuggestion}')">
                    <span>${s}</span>
                    <button class="insert-btn">+ Wstaw</button>
                </li>
            `;
        }).join('');

        return `
            <div class="ai-section">
                <h4><i class="fas fa-lightbulb"></i> Własne sugestie AI:</h4>
                <ul>${items}</ul>
            </div>
        `;
    }

    /**
     * Render detected issues
     */
    renderIssues(issues) {
        if (!issues || issues.length === 0) return '';

        const items = issues.map(i => `<li><i class="fas fa-exclamation-circle"></i> ${i}</li>`).join('');

        return `
            <div class="ai-section ai-issues">
                <h4><i class="fas fa-exclamation-triangle"></i> Wykryte problemy:</h4>
                <ul>${items}</ul>
            </div>
        `;
    }

    /**
     * Insert comment/suggestion into section textarea
     */
    insertCommentToSection(sectionId, text) {
        const textarea = document.getElementById(`feedback-${sectionId}`);
        if (!textarea) return;

        // Decode HTML entities
        const decodedText = this.decodeHtml(text);

        // Use the global insertCommentWithAnimation if available
        if (typeof insertCommentWithAnimation === 'function') {
            insertCommentWithAnimation(sectionId, decodedText);
        } else {
            // Fallback: simple insertion
            const startPos = textarea.selectionStart;
            const endPos = textarea.selectionEnd;
            const currentValue = textarea.value;

            let prefix = '';
            if (startPos > 0 && currentValue.charAt(startPos - 1) !== '\n') {
                prefix = '\n';
            }

            textarea.value = currentValue.substring(0, startPos) +
                prefix + decodedText +
                currentValue.substring(endPos);

            textarea.focus();

            if (typeof showToast === 'function') {
                showToast('Komentarz wstawiony', 'success');
            }
        }
    }

    /**
     * Get CSS class for quality score
     */
    getScoreClass(score) {
        if (score >= 70) return 'score-good';
        if (score >= 40) return 'score-medium';
        return 'score-low';
    }

    /**
     * Escape HTML special characters
     */
    escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Decode HTML entities
     */
    decodeHtml(text) {
        if (!text) return '';
        const textarea = document.createElement('textarea');
        textarea.innerHTML = text;
        return textarea.value;
    }

    /**
     * Learn from saved feedback (called when user saves)
     */
    async learnFromFeedback(sectionId, dmpContent, feedbackText, usedComments) {
        if (!this.enabled) return;

        try {
            await fetch('/api/ai/learn', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    section_id: sectionId,
                    dmp_content: dmpContent,
                    feedback_text: feedbackText,
                    used_comments: usedComments || []
                })
            });
        } catch (e) {
            console.error('AI learning error:', e);
        }
    }
}

// Create global instance
let aiAssistant = new AIAssistant();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on review page
    if (document.body.getAttribute('data-page') === 'review') {
        aiAssistant.init();
    }
});

// Export for global access
window.aiAssistant = aiAssistant;

console.log('AI Assistant module loaded');
