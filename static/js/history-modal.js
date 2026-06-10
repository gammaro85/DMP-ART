// ===========================================
// history-modal.js — Session History & Archive View
// Loaded on all pages: review, index, settings, documentation
// ===========================================

function _hmEsc(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;');
}

// ===========================================
// HISTORY MODAL
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
        // SessionManager may not exist on pages that don't load script.js
        const sessions = (typeof SessionManager !== 'undefined') ? SessionManager.getAllSessions() : [];
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
            const sid = session.session_id;
            return `
                <div class="session-item" data-session-id="${_hmEsc(sid)}">
                    <div class="session-info">
                        <div class="session-title" id="stitle-active-${_hmEsc(sid)}">${_hmEsc(displayName)}</div>
                        <div class="session-meta">
                            ${session.creation_date ? `<span><i class="fas fa-calendar"></i> ${_hmEsc(session.creation_date)}</span>` : ''}
                            <span><i class="fas fa-file"></i> ${_hmEsc(session.filename || '')}</span>
                        </div>
                        <div id="srename-active-${_hmEsc(sid)}" class="hidden"></div>
                    </div>
                    <div class="session-actions">
                        <button class="session-action-btn btn-rename"
                                aria-label="Zmień nazwę sesji" title="Zmień nazwę"
                                data-session-id="${_hmEsc(sid)}" data-session-type="active"
                                onclick="HistoryModal.showRenameForm(this)">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                        <button class="session-action-btn btn-view"
                                aria-label="Otwórz sesję" title="Otwórz sesję"
                                onclick="HistoryModal.openSession('${_hmEsc(sid)}')">
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
            const aid = archive.archive_id;
            const archivedDate = archive.archived_date ? new Date(archive.archived_date).toLocaleString('pl-PL') : '';
            return `
                <div class="session-item" data-archive-id="${_hmEsc(aid)}">
                    <div class="session-info">
                        <div class="session-title" id="stitle-archive-${_hmEsc(aid)}">${_hmEsc(displayName)}</div>
                        <div class="session-meta">
                            ${archivedDate ? `<span><i class="fas fa-archive"></i> ${_hmEsc(archivedDate)}</span>` : ''}
                            <span><i class="fas fa-file"></i> ${_hmEsc(archive.filename_original || '')}</span>
                        </div>
                        <div id="srename-archive-${_hmEsc(aid)}" class="hidden"></div>
                    </div>
                    <div class="session-actions">
                        <button class="session-action-btn btn-rename"
                                aria-label="Zmień nazwę archiwum" title="Zmień nazwę"
                                data-session-id="${_hmEsc(aid)}" data-session-type="archive"
                                onclick="HistoryModal.showRenameForm(this)">
                            <i class="fas fa-pencil-alt"></i>
                        </button>
                        <button class="session-action-btn btn-view"
                                aria-label="Podgląd archiwum" title="Podgląd"
                                onclick="HistoryModal.viewArchive('${_hmEsc(aid)}')">
                            <i class="fas fa-eye"></i> Podgląd
                        </button>
                        <button class="session-action-btn btn-delete"
                                aria-label="Usuń archiwum" title="Usuń archiwum"
                                onclick="HistoryModal.deleteArchive('${_hmEsc(aid)}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>`;
        }).join('');
        this.archivedSessions.innerHTML = `<div class="session-list">${html}</div>`;
    },

    // btn is the rename button element; reads session-id/type from data attributes
    // to avoid passing user-controlled strings through onclick JS literals
    showRenameForm(btn) {
        const sessionId   = btn.dataset.sessionId;
        const sessionType = btn.dataset.sessionType;
        const container   = document.getElementById(`srename-${sessionType}-${sessionId}`);
        const titleEl     = document.getElementById(`stitle-${sessionType}-${sessionId}`);
        if (!container) return;

        // Toggle: if already open, close it
        if (!container.classList.contains('hidden')) {
            container.classList.add('hidden');
            return;
        }

        // Current name from DOM — no escaping leakage
        const currentName = titleEl ? titleEl.textContent : '';

        container.innerHTML = `
            <div class="session-rename-form">
                <input type="text" id="rename-input-${_hmEsc(sessionId)}"
                       placeholder="Nazwa sesji..." maxlength="120">
                <button class="btn-confirm"
                        aria-label="Zatwierdź nazwę"
                        onclick="HistoryModal.saveRename('${_hmEsc(sessionId)}', '${_hmEsc(sessionType)}')">
                    <i class="fas fa-check"></i>
                </button>
                <button class="btn-cancel"
                        aria-label="Anuluj zmianę nazwy"
                        onclick="document.getElementById('srename-${_hmEsc(sessionType)}-${_hmEsc(sessionId)}').classList.add('hidden')">
                    <i class="fas fa-times"></i>
                </button>
            </div>`;

        // Set value via property to avoid any HTML injection
        const input = document.getElementById(`rename-input-${sessionId}`);
        if (input) {
            input.value = currentName;
            input.focus();
            input.select();
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.saveRename(sessionId, sessionType);
                if (e.key === 'Escape') container.classList.add('hidden');
            });
        }

        container.classList.remove('hidden');
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
                if (container) container.classList.add('hidden');
                if (typeof showToast === 'function') showToast('Nazwa zapisana', 'success');
            } else {
                if (typeof showToast === 'function') showToast('Błąd: ' + data.message, 'error');
            }
        } catch (error) {
            if (typeof showToast === 'function') showToast('Błąd połączenia', 'error');
        }
    },

    openSession(sessionId) {
        window.location.href = `/review?cache_id=${encodeURIComponent(sessionId)}`;
    },

    async viewArchive(archiveId) {
        try {
            const response = await fetch(`/api/restore-archived-session/${encodeURIComponent(archiveId)}`);
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
            const response = await fetch(`/api/delete-archived-session/${encodeURIComponent(archiveId)}`, { method: 'DELETE' });
            const data = await response.json();
            if (data.success) {
                const item = document.querySelector(`[data-archive-id="${_hmEsc(archiveId)}"]`);
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
    _currentFeedback: null,

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
                    <button class="archive-view-close" id="avm-close"
                            aria-label="Zamknij podgląd archiwum">&times;</button>
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
        const metaEl  = document.getElementById('avm-meta');
        const bodyEl  = document.getElementById('avm-body');
        if (!titleEl || !metaEl || !bodyEl) return;

        const displayName = metadata.session_name
            || (metadata.researcher_surname
                ? `${metadata.researcher_surname} ${metadata.researcher_firstname || ''}`.trim()
                : '')
            || metadata.filename_original
            || 'Archiwum';

        // Use textContent for the title to avoid XSS; prepend icon via DOM
        titleEl.textContent = '';
        const icon = document.createElement('i');
        icon.className = 'fas fa-archive';
        titleEl.appendChild(icon);
        titleEl.appendChild(document.createTextNode(' ' + displayName));

        const archivedDate = metadata.archived_date
            ? new Date(metadata.archived_date).toLocaleString('pl-PL') : '';

        // Build meta safely
        metaEl.innerHTML = [
            metadata.filename_original
                ? `<span><i class="fas fa-file"></i> ${_hmEsc(metadata.filename_original)}</span>` : '',
            archivedDate
                ? `<span><i class="fas fa-calendar"></i> Zarchiwizowano: ${_hmEsc(archivedDate)}</span>` : '',
            metadata.competition_name
                ? `<span><i class="fas fa-trophy"></i> ${_hmEsc(metadata.competition_name)}</span>` : ''
        ].filter(Boolean).join('');

        const sections = feedback.sections || {};
        const allSectionIds = ['1.1','1.2','2.1','2.2','3.1','3.2','4.1','4.2','5.1','5.2','5.3','5.4','6.1','6.2'];

        bodyEl.innerHTML = allSectionIds.map(id => {
            const text = sections[id] || '';
            const label = _hmEsc(SECTION_LABELS[id] || id);
            return `
                <div class="archive-view-section">
                    <div class="archive-view-section-header">
                        <span>${label}</span>
                        ${text ? '' : '<span style="font-weight:400;color:var(--text-muted);font-size:0.8rem">brak komentarza</span>'}
                    </div>
                    <div class="archive-view-section-body">
                        ${text
                            ? `<div class="feedback-text">${_hmEsc(text)}</div>`
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

document.addEventListener('DOMContentLoaded', () => {
    HistoryModal.init();
});

window.HistoryModal = HistoryModal;
window.ArchiveViewModal = ArchiveViewModal;
