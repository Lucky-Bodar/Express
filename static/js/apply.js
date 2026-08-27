// Helper functions for the apply page

function formatAadhaar(value) {
    const clean = (value || '').replace(/\D/g, '').slice(0, 12);
    const parts = clean.match(/.{1,4}/g);
    return parts ? parts.join(' ') : clean;
}

function validatePAN(value) {
    const regex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return regex.test((value || '').toUpperCase().trim());
}

function formatCardNumber(value) {
    const clean = (value || '').replace(/\D/g, '').slice(0, 16);
    const parts = clean.match(/.{1,4}/g);
    return parts ? parts.join(' ') : clean;
}

function showConfetti() {
    const colors = ['#e35d12', '#c2186f', '#2f6fae', '#ffffff', '#ffd700'];
    const container = document.createElement('div');
    container.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:9999;overflow:hidden;';
    document.body.appendChild(container);

    for (let i = 0; i < 40; i++) {
        const confetti = document.createElement('div');
        const size = 6 + Math.random() * 8;
        const color = colors[Math.floor(Math.random() * colors.length)];
        const startX = Math.random() * 100;
        const drift = (Math.random() - 0.5) * 200;
        const duration = 1.5 + Math.random() * 1.5;
        const delay = Math.random() * 0.5;

        confetti.style.cssText = `
            position:absolute;
            width:${size}px; height:${size}px;
            background:${color};
            border-radius:${Math.random() > 0.5 ? '50%' : '2px'};
            top:-20px; left:${startX}%;
            opacity:1;
            animation: confettiFall ${duration}s ease-out ${delay}s forwards;
        `;
        container.appendChild(confetti);
    }

    // Inject keyframes if not already present
    if (!document.getElementById('confetti-keyframes')) {
        const style = document.createElement('style');
        style.id = 'confetti-keyframes';
        style.textContent = `
            @keyframes confettiFall {
                0% { transform: translateY(0) rotate(0deg); opacity: 1; }
                100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    setTimeout(() => container.remove(), 4000);
}

function animateProgressBar(step, total) {
    const percentage = (step / total) * 100;
    const barFill = document.getElementById('progress-bar-fill');
    if (barFill) barFill.style.width = percentage + '%';

    const stepCounter = document.getElementById('step-counter');
    if (stepCounter) {
        stepCounter.textContent = `Step ${step} of ${total}`;
    }
}
