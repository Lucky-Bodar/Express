// Helper functions for the apply page

function formatAadhaar(value) {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,12}/g);
    const match = matches && matches[0] || '';
    const parts = [];

    for (let i = 0, len = match.length; i < len; i += 4) {
        parts.push(match.substring(i, i + 4));
    }

    if (parts.length) {
        return parts.join(' ');
    } else {
        return value;
    }
}

function validatePAN(value) {
    const regex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return regex.test(value.toUpperCase());
}

function formatCardNumber(value) {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || '';
    const parts = [];

    for (let i = 0, len = match.length; i < len; i += 4) {
        parts.push(match.substring(i, i + 4));
    }

    if (parts.length) {
        return parts.join(' ');
    } else {
        return value;
    }
}

function showConfetti() {
    const colors = ['#e35d12', '#c2186f', '#2f6fae', '#ffffff', '#ffd700'];
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100vw';
    container.style.height = '100vh';
    container.style.pointerEvents = 'none';
    container.style.zIndex = '9999';
    document.body.appendChild(container);

    for (let i = 0; i < 30; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'absolute';
        confetti.style.width = '10px';
        confetti.style.height = '10px';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.borderRadius = '50%';
        confetti.style.top = '50%';
        confetti.style.left = '50%';
        
        // Random destination
        const tx = (Math.random() - 0.5) * 500;
        const ty = (Math.random() - 0.5) * 500;
        
        container.appendChild(confetti);
        
        gsap.to(confetti, {
            x: tx,
            y: ty,
            opacity: 0,
            duration: 1.5 + Math.random(),
            ease: "power2.out",
            onComplete: () => {
                confetti.remove();
            }
        });
    }
    
    setTimeout(() => {
        container.remove();
    }, 3000);
}

function animateProgressBar(step, total) {
    const percentage = (step / total) * 100;
    gsap.to('#progress-bar-fill', {
        width: `${percentage}%`,
        duration: 0.5,
        ease: 'power2.inOut'
    });
    
    const stepCounter = document.getElementById('step-counter');
    if (stepCounter) {
        stepCounter.textContent = `Step ${step} of ${total}`;
    }
}
