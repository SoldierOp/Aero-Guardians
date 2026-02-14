// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar background on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 5px 20px rgba(0,0,0,0.1)';
    } else {
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    }
});

// Intersection Observer for animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.8s ease-out forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all cards and sections
document.querySelectorAll('.problem-card, .solution-card, .feature-card, .contact-card').forEach(el => {
    el.style.opacity = '0';
    observer.observe(el);
});

// Mobile menu toggle (add this if implementing hamburger menu)
const createMobileMenu = () => {
    const navMenu = document.querySelector('.nav-menu');
    const menuButton = document.createElement('button');
    menuButton.className = 'mobile-menu-toggle';
    menuButton.innerHTML = '☰';
    menuButton.style.display = 'none';
    
    if (window.innerWidth <= 768) {
        menuButton.style.display = 'block';
        document.querySelector('.navbar .container').prepend(menuButton);
        
        menuButton.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
};

// Stats counter animation
const animateStats = () => {
    const stats = document.querySelectorAll('.stat-value');
    stats.forEach(stat => {
        const target = stat.textContent.match(/\d+/)?.[0];
        if (!target) return;
        
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                stat.textContent = stat.textContent.replace(/\d+/, target);
                clearInterval(timer);
            } else {
                stat.textContent = stat.textContent.replace(/\d+/, Math.floor(current));
            }
        }, 30);
    });
};

// Run animations when hero is visible
const heroObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateStats();
            heroObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const hero = document.querySelector('.hero');
if (hero) {
    heroObserver.observe(hero);
}

// Initialize mobile menu check
window.addEventListener('resize', createMobileMenu);
createMobileMenu();

// Add loading state for dashboard link
const dashboardLinks = document.querySelectorAll('a[href="/dashboard"]');
dashboardLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        link.innerHTML = link.innerHTML + ' <span style="animation: spin 1s linear infinite">⟳</span>';
    });
});

// Spin animation for loading indicator
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

console.log('🌳 PeatGuard Pro - Protecting Indonesia\'s Peatlands');
console.log('GitHub: https://github.com/SoldierOp/Aero-Guardians');
