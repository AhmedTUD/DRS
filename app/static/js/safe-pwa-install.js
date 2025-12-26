/**
 * Safe PWA Install Button - Isolated implementation
 * Only appears on login page, cannot break layout
 */

(function() {
    'use strict';
    
    // Only run on login page
    const isLoginPage = window.location.pathname === '/auth/login' || 
                       window.location.pathname === '/login' || 
                       window.location.pathname === '/';
    
    if (!isLoginPage) {
        return;
    }
    
    class SafePWAInstaller {
        constructor() {
            this.deferredPrompt = null;
            this.installButton = null;
            this.isInstalled = false;
            
            try {
                this.init();
            } catch (error) {
                console.log('PWA installer error:', error);
            }
        }
        
        init() {
            // Check if already installed
            if (this.checkIfInstalled()) {
                return;
            }
            
            this.createButton();
            this.setupEventListeners();
            this.registerServiceWorker();
        }
        
        checkIfInstalled() {
            // Check if running in standalone mode
            if (window.matchMedia('(display-mode: standalone)').matches || 
                window.navigator.standalone === true) {
                this.isInstalled = true;
                return true;
            }
            return false;
        }
        
        createButton() {
            // Create button container
            this.installButton = document.createElement('div');
            this.installButton.className = 'drs-install-btn';
            this.installButton.innerHTML = `
                <img src="/static/icons/icon-192x192.png" alt="Install" class="drs-install-icon">
                <span class="drs-install-text">Install App</span>
            `;
            
            // Add styles
            this.addStyles();
            
            // Initially hidden
            this.installButton.style.display = 'none';
            
            // Add to body
            document.body.appendChild(this.installButton);
        }
        
        addStyles() {
            // Check if styles already added
            if (document.getElementById('drs-install-styles')) {
                return;
            }
            
            const style = document.createElement('style');
            style.id = 'drs-install-styles';
            style.textContent = `
                .drs-install-btn {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 12px 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 50px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    user-select: none;
                    -webkit-user-select: none;
                    -webkit-tap-highlight-color: transparent;
                    opacity: 0;
                    transform: translateY(20px);
                }
                
                .drs-install-btn.drs-show {
                    opacity: 1;
                    transform: translateY(0);
                }
                
                .drs-install-btn:hover {
                    transform: translateY(-2px) scale(1.02);
                    box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
                    background: linear-gradient(135deg, #7c8ef0 0%, #8a5cb8 100%);
                }
                
                .drs-install-btn:active {
                    transform: translateY(0) scale(0.98);
                }
                
                .drs-install-icon {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    flex-shrink: 0;
                }
                
                .drs-install-text {
                    white-space: nowrap;
                }
                
                .drs-install-btn.drs-installing .drs-install-text::after {
                    content: '...';
                    animation: drs-dots 1.5s infinite;
                }
                
                @keyframes drs-dots {
                    0%, 20% { content: ''; }
                    40% { content: '.'; }
                    60% { content: '..'; }
                    80%, 100% { content: '...'; }
                }
                
                @media (max-width: 768px) {
                    .drs-install-btn {
                        bottom: 15px;
                        right: 15px;
                        padding: 10px 16px;
                        font-size: 13px;
                    }
                    
                    .drs-install-icon {
                        width: 18px;
                        height: 18px;
                    }
                }
                
                /* Hide in standalone mode */
                @media all and (display-mode: standalone) {
                    .drs-install-btn {
                        display: none !important;
                    }
                }
            `;
            
            document.head.appendChild(style);
        }
        
        setupEventListeners() {
            // Listen for beforeinstallprompt
            window.addEventListener('beforeinstallprompt', (e) => {
                console.log('beforeinstallprompt event fired');
                e.preventDefault();
                this.deferredPrompt = e;
                this.showButton();
            });
            
            // Listen for app installed
            window.addEventListener('appinstalled', () => {
                console.log('App installed');
                this.hideButton();
                this.isInstalled = true;
            });
            
            // Button click handler
            if (this.installButton) {
                this.installButton.addEventListener('click', () => {
                    this.handleInstall();
                });
            }
            
            // Show button after delay - always show for testing
            setTimeout(() => {
                if (!this.isInstalled) {
                    console.log('Showing install button after delay');
                    this.showButton();
                }
            }, 1000);
        }
        
        showButton() {
            if (this.installButton && !this.isInstalled) {
                this.installButton.style.display = 'flex';
                setTimeout(() => {
                    this.installButton.classList.add('drs-show');
                }, 100);
            }
        }
        
        hideButton() {
            if (this.installButton) {
                this.installButton.classList.remove('drs-show');
                setTimeout(() => {
                    this.installButton.style.display = 'none';
                }, 300);
            }
        }
        
        async handleInstall() {
            if (!this.installButton) return;
            
            console.log('Install button clicked, deferredPrompt:', !!this.deferredPrompt);
            
            try {
                if (this.deferredPrompt) {
                    console.log('Using deferred prompt');
                    
                    // Show installing state
                    this.installButton.classList.add('drs-installing');
                    this.installButton.querySelector('.drs-install-text').textContent = 'Installing';
                    
                    // Show native prompt
                    const promptResult = await this.deferredPrompt.prompt();
                    console.log('Prompt result:', promptResult);
                    
                    const { outcome } = await this.deferredPrompt.userChoice;
                    console.log('User choice:', outcome);
                    
                    if (outcome === 'accepted') {
                        console.log('User accepted install');
                        this.hideButton();
                        this.isInstalled = true;
                    } else {
                        console.log('User dismissed install');
                        this.resetButton();
                    }
                    
                    this.deferredPrompt = null;
                } else {
                    console.log('No deferred prompt, showing manual instructions');
                    // Show manual instructions
                    this.showInstructions();
                }
            } catch (error) {
                console.log('Install error:', error);
                this.resetButton();
            }
        }
        
        resetButton() {
            if (this.installButton) {
                this.installButton.classList.remove('drs-installing');
                this.installButton.querySelector('.drs-install-text').textContent = 'Install App';
            }
        }
        
        showInstructions() {
            const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
            const message = isIOS 
                ? 'To install: Tap Share → Add to Home Screen'
                : 'To install: Look for install option in your browser menu';
            
            // Simple alert for now - can be enhanced later
            alert(message);
        }
        
        async registerServiceWorker() {
            if ('serviceWorker' in navigator) {
                try {
                    await navigator.serviceWorker.register('/static/sw.js');
                } catch (error) {
                    console.log('Service worker registration failed:', error);
                }
            }
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new SafePWAInstaller();
        });
    } else {
        new SafePWAInstaller();
    }
    
})();