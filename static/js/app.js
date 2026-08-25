/* ══════════════════════════════════════════════
   EXPRESS — Core Application JavaScript
   ══════════════════════════════════════════════ */

/* ── Page Transition Manager ── */
function navigateTo(url) {
  var body = document.body;
  body.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
  body.style.opacity = '0';
  body.style.transform = 'scale(0.98)';
  setTimeout(function() {
    window.location.href = url;
  }, 350);
}

/* ── Page Entrance Animation ── */
document.addEventListener('DOMContentLoaded', function() {
  document.body.style.opacity = '0';
  document.body.style.transform = 'translateY(12px)';
  requestAnimationFrame(function() {
    document.body.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    document.body.style.opacity = '1';
    document.body.style.transform = 'translateY(0)';
  });

  // Keep application hand-offs intentional and polished wherever an Apply
  // button appears on the marketing experience.
  document.querySelectorAll('a[href="/apply"], a[href="/dashboard"]').forEach(function(link) {
    link.addEventListener('click', function(event) {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || link.target === '_blank') return;
      event.preventDefault();
      navigateTo(link.href);
    });
  });
});

/* ── Step Flow Controller ── */
function StepFlow(containerSelector) {
  this.container = document.querySelector(containerSelector);
  this.steps = this.container ? this.container.querySelectorAll('.step') : [];
  this.current = 0;
  this.init();
}

StepFlow.prototype.init = function() {
  var self = this;
  this.steps.forEach(function(step, i) {
    if (i === 0) {
      step.classList.add('active');
      step.style.display = 'block';
      step.style.opacity = '1';
      step.style.transform = 'translateX(0)';
    } else {
      step.style.display = 'none';
      step.style.opacity = '0';
      step.style.transform = 'translateX(60px)';
    }
  });
};

StepFlow.prototype.goTo = function(index) {
  if (index === this.current || index < 0 || index >= this.steps.length) return;
  var currentStep = this.steps[this.current];
  var nextStep = this.steps[index];
  var direction = index > this.current ? 1 : -1;

  // Exit current
  gsap.to(currentStep, {
    opacity: 0,
    x: -60 * direction,
    duration: 0.35,
    ease: 'power2.in',
    onComplete: function() {
      currentStep.style.display = 'none';
      currentStep.classList.remove('active');
    }
  });

  // Enter next
  nextStep.style.display = 'block';
  nextStep.classList.add('active');
  gsap.fromTo(nextStep,
    { opacity: 0, x: 60 * direction },
    { opacity: 1, x: 0, duration: 0.45, ease: 'power2.out', delay: 0.15 }
  );

  this.current = index;
  
  // Update progress bar if present
  var progressBar = document.getElementById('progress-fill');
  if (progressBar) {
    var percent = ((index + 1) / this.steps.length) * 100;
    gsap.to(progressBar, { width: percent + '%', duration: 0.5, ease: 'power2.out' });
  }
  
  var stepText = document.getElementById('step-text');
  if (stepText) {
    stepText.textContent = 'Step ' + (index + 1) + ' of ' + this.steps.length;
  }
};

StepFlow.prototype.next = function() {
  this.goTo(this.current + 1);
};

StepFlow.prototype.prev = function() {
  this.goTo(this.current - 1);
};

/* ── API Helper ── */
function api(url, data) {
  var options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  };
  return fetch(url, options).then(function(res) { return res.json(); });
}

function apiGet(url) {
  return fetch(url).then(function(res) { return res.json(); });
}

/* ── Format Indian Number ── */
function formatIndian(num) {
  num = parseInt(num) || 0;
  var str = num.toString();
  var lastThree = str.substring(str.length - 3);
  var otherNumbers = str.substring(0, str.length - 3);
  if (otherNumbers !== '') {
    lastThree = ',' + lastThree;
  }
  return otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + lastThree;
}

/* ── Toast Notification ── */
function showToast(message, type) {
  type = type || 'success';
  var toast = document.createElement('div');
  toast.className = 'fixed top-20 left-1/2 -translate-x-1/2 z-[200] px-5 py-3 rounded-2xl shadow-lg text-[13px] font-medium transition-all duration-300';
  
  if (type === 'success') {
    toast.style.background = '#0d0d0f';
    toast.style.color = '#fbfbfa';
  } else if (type === 'error') {
    toast.style.background = '#dc2626';
    toast.style.color = '#ffffff';
  }
  
  toast.textContent = message;
  toast.style.opacity = '0';
  toast.style.transform = 'translate(-50%, -10px)';
  document.body.appendChild(toast);
  
  requestAnimationFrame(function() {
    toast.style.opacity = '1';
    toast.style.transform = 'translate(-50%, 0)';
  });
  
  setTimeout(function() {
    toast.style.opacity = '0';
    toast.style.transform = 'translate(-50%, -10px)';
    setTimeout(function() { toast.remove(); }, 300);
  }, 3000);
}

/* ── Modal ── */
function showModal(id) {
  var modal = document.getElementById(id);
  if (!modal) return;
  modal.style.display = 'flex';
  requestAnimationFrame(function() {
    modal.style.opacity = '1';
    var content = modal.querySelector('.modal-content');
    if (content) {
      content.style.transform = 'translateY(0) scale(1)';
      content.style.opacity = '1';
    }
  });
}

function hideModal(id) {
  var modal = document.getElementById(id);
  if (!modal) return;
  var content = modal.querySelector('.modal-content');
  if (content) {
    content.style.transform = 'translateY(16px) scale(0.96)';
    content.style.opacity = '0';
  }
  modal.style.opacity = '0';
  setTimeout(function() { modal.style.display = 'none'; }, 300);
}

/* ── Text Reveal Observer ── */
function initTextReveals() {
  var revealEls = document.querySelectorAll('.text-reveal');
  if (!revealEls.length) return;
  
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        var idx = Array.from(revealEls).indexOf(entry.target);
        entry.target.style.transitionDelay = (idx % 4) * 0.1 + 's';
      }
    });
  }, { threshold: 0.15 });
  
  revealEls.forEach(function(el) { observer.observe(el); });
}

/* ── Pulse Ring Animations ── */
function initPulseRings() {
  document.querySelectorAll('.pulse-anim').forEach(function(ring, i) {
    ring.style.animation = 'pulse-ring 2.2s cubic-bezier(0.4, 0, 0.2, 1) infinite';
    ring.style.animationDelay = i * 0.7 + 's';
  });
}

/* ── Initialize Common ── */
document.addEventListener('DOMContentLoaded', function() {
  initTextReveals();
  initPulseRings();
});

/* ── Logout ── */
function logout() {
  document.cookie = 'express_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  navigateTo('/login');
}
