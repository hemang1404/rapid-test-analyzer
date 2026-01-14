/**
 * Dark Mode Toggle System
 * Manages dark mode state across all pages with localStorage persistence
 */

class DarkModeManager {
    constructor() {
        this.storageKey = 'rapidTestAnalyzer_darkMode';
        this.isDark = this.getStoredPreference();
        this.init();
    }

    getStoredPreference() {
        const stored = localStorage.getItem(this.storageKey);
        if (stored !== null) {
            return stored === 'true';
        }
        // Check system preference
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    init() {
        // Apply dark mode on page load
        this.applyDarkMode(this.isDark);
        
        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
                if (localStorage.getItem(this.storageKey) === null) {
                    this.toggle(e.matches);
                }
            });
        }
    }

    toggle(forceDark = null) {
        this.isDark = forceDark !== null ? forceDark : !this.isDark;
        localStorage.setItem(this.storageKey, this.isDark);
        this.applyDarkMode(this.isDark);
        
        // Dispatch event for other components to listen
        window.dispatchEvent(new CustomEvent('darkModeChanged', { detail: { isDark: this.isDark } }));
    }

    applyDarkMode(isDark) {
        const html = document.documentElement;
        
        if (isDark) {
            html.classList.add('dark');
            document.body.classList.add('dark-mode');
        } else {
            html.classList.remove('dark');
            document.body.classList.remove('dark-mode');
        }

        // Update meta theme color for mobile browsers
        this.updateMetaTheme(isDark);
    }

    updateMetaTheme(isDark) {
        let metaTheme = document.querySelector('meta[name="theme-color"]');
        if (!metaTheme) {
            metaTheme = document.createElement('meta');
            metaTheme.name = 'theme-color';
            document.head.appendChild(metaTheme);
        }
        metaTheme.content = isDark ? '#1e293b' : '#07361f';
    }

    createToggleButton(container = null) {
        const button = document.createElement('button');
        button.id = 'darkModeToggle';
        button.className = 'dark-mode-toggle glass rounded-lg px-3 py-2 hover:bg-white/20 transition-all duration-200 flex items-center gap-2';
        button.setAttribute('aria-label', 'Toggle dark mode');
        button.title = 'Toggle dark mode';
        
        this.updateButtonContent(button);
        
        button.addEventListener('click', () => {
            this.toggle();
            this.updateButtonContent(button);
        });

        if (container) {
            container.appendChild(button);
        }
        
        return button;
    }

    updateButtonContent(button) {
        if (this.isDark) {
            button.innerHTML = `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                </svg>
                <span class="text-sm hidden sm:inline">Light</span>
            `;
        } else {
            button.innerHTML = `
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                </svg>
                <span class="text-sm hidden sm:inline">Dark</span>
            `;
        }
    }
}

// Initialize dark mode manager
const darkModeManager = new DarkModeManager();

// Auto-inject toggle button into header if it exists
document.addEventListener('DOMContentLoaded', () => {
    // Try to find a suitable container for the toggle button
    const possibleContainers = [
        document.querySelector('.fixed.top-4.right-4'),  // Fixed top-right div (most pages)
        document.querySelector('header .flex.items-center.gap-4'),
        document.querySelector('header .container > div'),
        document.querySelector('.no-print .flex.justify-center.gap-4'),
        document.querySelector('header')
    ];

    const container = possibleContainers.find(el => el !== null);
    
    if (container) {
        darkModeManager.createToggleButton(container);
    }
});

// Export for use in other scripts
window.darkModeManager = darkModeManager;
