// Dark Mode Toggle Functionality for DMP ART
// Add this to your existing script.js or create a separate dark-mode.js file

document.addEventListener('DOMContentLoaded', function () {
    initializeDarkMode();
});

function initializeDarkMode() {
    // Create the dark mode toggle button
    createDarkModeToggle();

    // Load saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('dmp-art-theme') || 'light';
    setTheme(savedTheme);

    // Update toggle button state
    updateToggleButton(savedTheme);
}

function createDarkModeToggle() {
    // Check if toggle already exists
    if (document.querySelector('.theme-toggle')) {
        return;
    }

    const toggle = document.createElement('button');
    toggle.className = 'theme-toggle';
    toggle.setAttribute('aria-label', 'Toggle dark mode');
    toggle.setAttribute('title', 'Switch between light and dark modes');

    toggle.innerHTML = `
        <span class="icon" id="theme-icon">🌙</span>
        <span id="theme-text">Dark</span>
    `;

    // Add click event listener
    toggle.addEventListener('click', function () {
        toggleTheme();
    });

    // Add keyboard support
    toggle.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleTheme();
        }
    });

    // Append to body
    document.body.appendChild(toggle);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    setTheme(newTheme);
    updateToggleButton(newTheme);

    // Save preference
    localStorage.setItem('dmp-art-theme', newTheme);

    // Show notification
    showThemeChangeNotification(newTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);

    // Update meta theme-color for mobile browsers
    updateMetaThemeColor(theme);
}

function updateToggleButton(theme) {
    const icon = document.getElementById('theme-icon');
    const text = document.getElementById('theme-text');

    if (icon && text) {
        if (theme === 'dark') {
            icon.textContent = '☀️';
            text.textContent = 'Light';
        } else {
            icon.textContent = '🌙';
            text.textContent = 'Dark';
        }
    }
}

function updateMetaThemeColor(theme) {
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');

    if (!metaThemeColor) {
        metaThemeColor = document.createElement('meta');
        metaThemeColor.name = 'theme-color';
        document.head.appendChild(metaThemeColor);
    }

    if (theme === 'dark') {
        metaThemeColor.content = '#121212';
    } else {
        metaThemeColor.content = '#ffffff';
    }
}

function showThemeChangeNotification(theme) {
    // Check if we have the toast system available
    if (typeof showToast === 'function') {
        const message = theme === 'dark' ? '🌙 Dark mode enabled' : '☀️ Light mode enabled';
        showToast(message);
    } else {
        // Fallback notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background-color: ${theme === 'dark' ? '#333' : '#fff'};
            color: ${theme === 'dark' ? '#fff' : '#333'};
            padding: 10px 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 10000;
            font-size: 14px;
            border: 1px solid ${theme === 'dark' ? '#555' : '#ddd'};
        `;

        const message = theme === 'dark' ? '🌙 Dark mode enabled' : '☀️ Light mode enabled';
        notification.textContent = message;

        document.body.appendChild(notification);

        // Remove after 2 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 2000);
    }
}

// Auto-detect system preference if no saved preference exists
function detectSystemPreference() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

// Listen for system theme changes
if (window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    mediaQuery.addEventListener('change', function (e) {
        // Only auto-switch if user hasn't manually set a preference
        if (!localStorage.getItem('dmp-art-theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            setTheme(newTheme);
            updateToggleButton(newTheme);
        }
    });
}

// Enhanced functionality for better UX
function addDarkModeKeyboardShortcut() {
    document.addEventListener('keydown', function (e) {
        // Ctrl/Cmd + Shift + D to toggle dark mode
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
            e.preventDefault();
            toggleTheme();
        }
    });
}

// Initialize keyboard shortcut
document.addEventListener('DOMContentLoaded', function () {
    addDarkModeKeyboardShortcut();
});

// Utility function to get current theme
function getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
}

// Function to force a specific theme (useful for testing)
function forceTheme(theme) {
    if (theme === 'dark' || theme === 'light') {
        setTheme(theme);
        updateToggleButton(theme);
        localStorage.setItem('dmp-art-theme', theme);
    }
}

// Export functions for use in other parts of the application
window.DarkMode = {
    toggle: toggleTheme,
    setTheme: setTheme,
    getCurrentTheme: getCurrentTheme,
    forceTheme: forceTheme
};