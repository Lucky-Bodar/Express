// KYC verification helpers

function createLoaderDOM() {
    let loader = document.getElementById('kyc-loader-overlay');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'kyc-loader-overlay';
        loader.className = 'fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm opacity-0 pointer-events-none transition-opacity duration-300';
        
        loader.innerHTML = `
            <div class="relative w-20 h-20 mb-6 flex items-center justify-center">
                <div id="kyc-spinner" class="absolute inset-0 border-4 border-white/20 border-t-[#e35d12] rounded-full animate-spin"></div>
                <div id="kyc-success-icon" class="hidden text-emerald-400 transform scale-110">
                    <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                </div>
                <div id="kyc-error-icon" class="hidden text-red-400 transform scale-110">
                    <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"></path></svg>
                </div>
            </div>
            <p id="kyc-loader-message" class="text-white text-xl font-medium tracking-wide text-center px-4"></p>
        `;
        document.body.appendChild(loader);
    }
    return loader;
}

function showVerificationLoader(message) {
    try {
        const loader = createLoaderDOM();
        const spinner = document.getElementById('kyc-spinner');
        const successIcon = document.getElementById('kyc-success-icon');
        const errorIcon = document.getElementById('kyc-error-icon');
        const messageEl = document.getElementById('kyc-loader-message');

        if (spinner) spinner.classList.remove('hidden');
        if (successIcon) successIcon.classList.add('hidden');
        if (errorIcon) errorIcon.classList.add('hidden');
        
        if (messageEl) {
            messageEl.textContent = message || 'Verifying...';
            messageEl.className = 'text-white text-xl font-medium tracking-wide text-center px-4';
        }
        
        loader.classList.remove('opacity-0', 'pointer-events-none');
        loader.classList.add('opacity-100', 'pointer-events-auto');
    } catch (e) {
        console.error('showVerificationLoader error:', e);
    }
}

function hideVerificationLoader() {
    try {
        const loader = document.getElementById('kyc-loader-overlay');
        if (loader) {
            loader.classList.remove('opacity-100', 'pointer-events-auto');
            loader.classList.add('opacity-0', 'pointer-events-none');
        }
    } catch (e) {
        console.error('hideVerificationLoader error:', e);
    }
}

function showVerificationSuccess(message) {
    return new Promise((resolve) => {
        try {
            const loader = createLoaderDOM();
            const spinner = document.getElementById('kyc-spinner');
            const successIcon = document.getElementById('kyc-success-icon');
            const errorIcon = document.getElementById('kyc-error-icon');
            const messageEl = document.getElementById('kyc-loader-message');

            if (spinner) spinner.classList.add('hidden');
            if (errorIcon) errorIcon.classList.add('hidden');
            if (successIcon) successIcon.classList.remove('hidden');

            if (messageEl) {
                messageEl.textContent = message || 'Verified ✓';
                messageEl.className = 'text-emerald-400 text-xl font-medium tracking-wide text-center px-4';
            }

            setTimeout(() => {
                hideVerificationLoader();
                setTimeout(resolve, 300);
            }, 1200);
        } catch (e) {
            console.error('showVerificationSuccess error:', e);
            hideVerificationLoader();
            resolve();
        }
    });
}

function showVerificationError(message) {
    return new Promise((resolve) => {
        try {
            const loader = createLoaderDOM();
            const spinner = document.getElementById('kyc-spinner');
            const successIcon = document.getElementById('kyc-success-icon');
            const errorIcon = document.getElementById('kyc-error-icon');
            const messageEl = document.getElementById('kyc-loader-message');

            if (spinner) spinner.classList.add('hidden');
            if (successIcon) successIcon.classList.add('hidden');
            if (errorIcon) errorIcon.classList.remove('hidden');

            if (messageEl) {
                messageEl.textContent = message || 'Verification Failed';
                messageEl.className = 'text-red-400 text-xl font-medium tracking-wide text-center px-4';
            }

            setTimeout(() => {
                hideVerificationLoader();
                setTimeout(resolve, 300);
            }, 1500);
        } catch (e) {
            console.error('showVerificationError error:', e);
            hideVerificationLoader();
            resolve();
        }
    });
}
