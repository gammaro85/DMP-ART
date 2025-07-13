// static/js/dark-mode.js - ENHANCED & CONSOLIDATED
(function () {
    'use strict';

    // Dark Mode Module
    const DarkMode = {
        STORAGE_KEY: 'dmp-art-theme',
        LIGHT_THEME: 'light',
        DARK_THEME: 'dark',

        init() {
            this.createToggleButton();
            this.loadTheme();
            this.setupEventListeners();
            this.setupKeyboardShortcuts();
        },

        loadTheme() {
            const savedTheme = localStorage.getItem(this.STORAGE_KEY);
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const theme = savedTheme || (prefersDark ? this.DARK_THEME : this.LIGHT_THEME);

            this.setTheme(theme);
            this.updateToggleButton(theme === this.DARK_THEME);
        },

        setTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            this.updateMetaThemeColor(theme);
        },

        toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === this.DARK_THEME ? this.LIGHT_THEME : this.DARK_THEME;

            this.setTheme(newTheme);
            this.updateToggleButton(newTheme === this.DARK_THEME);
            localStorage.setItem(this.STORAGE_KEY, newTheme);
        },

        createToggleButton() {
            // Check if button already exists
            if (document.querySelector('.theme-toggle')) return;

            const button = document.createElement('button');
            button.className = 'theme-toggle';
            button.setAttribute('aria-label', 'Toggle dark mode');
            button.innerHTML = `
                <span id="theme-text">Dark</span>
            `;

            button.addEventListener('click', () => this.toggleTheme());
            document.body.appendChild(button);
        },

        updateToggleButton(isDark) {
            const text = document.getElementById('theme-text');

            if (text) {
                text.textContent = isDark ? 'Light Mode' : 'Dark Mode';
            }
        },

        updateMetaThemeColor(theme) {
            let meta = document.querySelector('meta[name="theme-color"]');
            if (!meta) {
                meta = document.createElement('meta');
                meta.name = 'theme-color';
                document.head.appendChild(meta);
            }
            meta.content = theme === this.DARK_THEME ? '#121212' : '#ffffff';
        },

        setupEventListeners() {
            // Listen for system theme changes
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                if (!localStorage.getItem(this.STORAGE_KEY)) {
                    const theme = e.matches ? this.DARK_THEME : this.LIGHT_THEME;
                    this.setTheme(theme);
                    this.updateToggleButton(theme === this.DARK_THEME);
                }
            });
        },

        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + Shift + D
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                    e.preventDefault();
                    this.toggleTheme();
                }
            });
        }
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => DarkMode.init());
    } else {
        DarkMode.init();
    }

    // Export for global use
    window.DarkMode = DarkMode;
})();