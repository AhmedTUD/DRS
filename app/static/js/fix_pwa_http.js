// إصلاح PWA للعمل مع HTTP
// هذا الملف سيحل مشكلة PWA مع HTTP

// تحقق من دعم PWA
function checkPWASupport() {
    const isHTTPS = location.protocol === 'https:';
    const isLocalhost = location.hostname === 'localhost' || location.hostname === '127.0.0.1';
    const supportsServiceWorker = 'serviceWorker' in navigator;
    const supportsManifest = 'manifest' in document.createElement('link');
    
    console.log('PWA Support Check:', {
        isHTTPS,
        isLocalhost,
        supportsServiceWorker,
        supportsManifest,
        canInstall: (isHTTPS || isLocalhost) && supportsServiceWorker && supportsManifest
    });
    
    return {
        canInstall: (isHTTPS || isLocalhost) && supportsServiceWorker && supportsManifest,
        reason: !isHTTPS && !isLocalhost ? 'HTTPS required' : 
                !supportsServiceWorker ? 'Service Worker not supported' :
                !supportsManifest ? 'Manifest not supported' : 'OK'
    };
}

// تسجيل Service Worker مع معالجة الأخطاء
function registerServiceWorker() {
    const support = checkPWASupport();
    
    if (!support.canInstall) {
        console.log('PWA installation not available:', support.reason);
        showPWAMessage('PWA installation requires HTTPS or localhost');
        return;
    }
    
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('Service Worker registered successfully:', registration);
                
                // تحقق من إمكانية التثبيت
                window.addEventListener('beforeinstallprompt', (e) => {
                    console.log('PWA install prompt available');
                    e.preventDefault();
                    window.deferredPrompt = e;
                    showInstallButton();
                });
                
                // تحقق من التثبيت
                window.addEventListener('appinstalled', (e) => {
                    console.log('PWA installed successfully');
                    hideInstallButton();
                    showPWAMessage('App installed successfully!');
                });
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
                showPWAMessage('PWA features not available');
            });
    }
}

// عرض رسالة PWA
function showPWAMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'alert alert-info alert-dismissible fade show';
    messageDiv.innerHTML = `
        <i class="fas fa-info-circle"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(messageDiv, container.firstChild);
    
    // إخفاء الرسالة بعد 5 ثوان
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

// عرض زر التثبيت
function showInstallButton() {
    let installBtn = document.getElementById('pwa-install-btn');
    
    if (!installBtn) {
        installBtn = document.createElement('button');
        installBtn.id = 'pwa-install-btn';
        installBtn.className = 'btn btn-primary btn-sm position-fixed';
        installBtn.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000;';
        installBtn.innerHTML = '<i class="fas fa-download"></i> Install App';
        
        installBtn.addEventListener('click', installPWA);
        document.body.appendChild(installBtn);
    }
    
    installBtn.style.display = 'block';
}

// إخفاء زر التثبيت
function hideInstallButton() {
    const installBtn = document.getElementById('pwa-install-btn');
    if (installBtn) {
        installBtn.style.display = 'none';
    }
}

// تثبيت PWA
function installPWA() {
    if (window.deferredPrompt) {
        window.deferredPrompt.prompt();
        
        window.deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            } else {
                console.log('User dismissed the install prompt');
            }
            window.deferredPrompt = null;
        });
    } else {
        // إذا لم يكن متاحاً، اعرض تعليمات يدوية
        showManualInstallInstructions();
    }
}

// عرض تعليمات التثبيت اليدوي
function showManualInstallInstructions() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Install App</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <h6>Chrome/Edge:</h6>
                    <p>1. Click the three dots menu (⋮)<br>
                       2. Select "Install Daily Report System..."<br>
                       3. Click "Install"</p>
                    
                    <h6>Firefox:</h6>
                    <p>1. Click the address bar<br>
                       2. Look for the install icon (+)<br>
                       3. Click to install</p>
                    
                    <h6>Safari (iOS):</h6>
                    <p>1. Tap the share button<br>
                       2. Select "Add to Home Screen"<br>
                       3. Tap "Add"</p>
                    
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Note:</strong> HTTPS is required for full PWA features. 
                        Some browsers may not show install option over HTTP.
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // حذف المودال بعد الإغلاق
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

// تشغيل عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    registerServiceWorker();
    
    // إضافة زر تثبيت يدوي إذا لم يكن متاحاً تلقائياً
    setTimeout(() => {
        if (!window.deferredPrompt && !document.getElementById('pwa-install-btn')) {
            const support = checkPWASupport();
            if (!support.canInstall) {
                // عرض زر للتعليمات اليدوية
                const manualBtn = document.createElement('button');
                manualBtn.className = 'btn btn-outline-primary btn-sm position-fixed';
                manualBtn.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000;';
                manualBtn.innerHTML = '<i class="fas fa-mobile-alt"></i> Install Guide';
                manualBtn.addEventListener('click', showManualInstallInstructions);
                document.body.appendChild(manualBtn);
            }
        }
    }, 3000);
});