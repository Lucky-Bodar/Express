// dashboard.js

function formatIndianNumber(num) {
    if (num === null || num === undefined) return '0';
    let str = num.toString();
    let lastThree = str.substring(str.length - 3);
    let otherNumbers = str.substring(0, str.length - 3);
    if (otherNumbers != '') {
        lastThree = ',' + lastThree;
    }
    return otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + lastThree;
}

function calculateEMI(principal, rate, months) {
    let p = parseFloat(principal);
    let r = parseFloat(rate) / 100;
    let n = parseInt(months);
    let emi = p * r * Math.pow(1 + r, n) / (Math.pow(1 + r, n) - 1);
    let totalAmount = emi * n;
    let totalInterest = totalAmount - p;
    return {
        emi: Math.round(emi),
        totalInterest: Math.round(totalInterest),
        totalAmount: Math.round(totalAmount)
    };
}

function animateCounter(element, from, to, duration) {
    let obj = { val: from };
    gsap.to(obj, {
        val: to,
        duration: duration / 1000,
        ease: "power2.out",
        onUpdate: function() {
            element.innerText = '₹' + formatIndianNumber(Math.floor(obj.val));
        }
    });
}
