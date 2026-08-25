// KYC verification helpers

function createLoaderDOM() {
    let loader = document.getElementById('kyc-loader-overlay');
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'kyc-loader-overlay';
        loader.className = 'fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm opacity-0 pointer-events-none transition-opacity duration-300';
        
        loader.innerHTML = `
            <div class="relative w-20 h-20 mb-6">
                <div class="absolute inset-0 border-4 border-white/20 rounded-full"></div>
                <div class="absolute inset-0 border-4 border-[#e35d12] rounded-full border-t-transparent animate-spin"></div>
                <div id="kyc-success-icon" class="absolute inset-0 flex items-center justify-center opacity-0 scale-50 transition-all duration-300 text-green-500">
                    <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
                </div>
                <div id="kyc-error-icon" class="absolute inset-0 flex items-center justify-center opacity-0 scale-50 transition-all duration-300 text-red-500">
                    <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"></path></svg>
                </div>
            </div>
            <p id="kyc-loader-message" class="text-white text-xl font-medium tracking-wide"></p>
        `;
        document.body.appendChild(loader);
    }
    return loader;
}

function showVerificationLoader(message) {
    const loader = createLoaderDOM();
    const messageEl = document.getElementById('kyc-loader-message');
    const spinner = loader.querySelector('.animate-spin').parentElement;
    const successIcon = document.getElementById('kyc-success-icon');
    const errorIcon = document.getElementById('kyc-error-icon');
    
    // Reset state
    spinner.style.opacity = '1';
    successIcon.classList.remove('opacity-100', 'scale-100');
    successIcon.classList.add('opacity-0', 'scale-50');
    errorIcon.classList.remove('opacity-100', 'scale-100');
    errorIcon.classList.add('opacity-0', 'scale-50');
    
    messageEl.textContent = message;
    messageEl.className = 'text-white text-xl font-medium tracking-wide';
    
    loader.classList.remove('opacity-0', 'pointer-events-none');
    loader.classList.add('opacity-100', 'pointer-events-auto');
}

function hideVerificationLoader() {
    const loader = document.getElementById('kyc-loader-overlay');
    if (loader) {
        loader.classList.remove('opacity-100', 'pointer-events-auto');
        loader.classList.add('opacity-0', 'pointer-events-none');
    }
}

function showVerificationSuccess(message) {
    return new Promise((resolve) => {
        const loader = document.getElementById('kyc-loader-overlay');
        const messageEl = document.getElementById('kyc-loader-message');
        const spinner = loader.querySelector('.animate-spin').parentElement;
        const successIcon = document.getElementById('kyc-success-icon');
        
        spinner.style.opacity = '0';
        successIcon.classList.remove('opacity-0', 'scale-50');
        successIcon.classList.add('opacity-100', 'scale-100');
        
        messageEl.textContent = message;
        messageEl.classList.add('text-green-400');
        
        setTimeout(() => {
            hideVerificationLoader();
            setTimeout(resolve, 300); // Wait for fade out
        }, 1500);
    });
}

function showVerificationError(message) {
    return new Promise((resolve) => {
        const loader = document.getElementById('kyc-loader-overlay');
        const messageEl = document.getElementById('kyc-loader-message');
        const spinner = loader.querySelector('.animate-spin').parentElement;
        const errorIcon = document.getElementById('kyc-error-icon');
        
        spinner.style.opacity = '0';
        errorIcon.classList.remove('opacity-0', 'scale-50');
        errorIcon.classList.add('opacity-100', 'scale-100');
        
        messageEl.textContent = message;
        messageEl.classList.add('text-red-400');
        
        setTimeout(() => {
            hideVerificationLoader();
            setTimeout(resolve, 300);
        }, 2000);
    });
}
