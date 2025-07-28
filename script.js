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

// Contact form handling
document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Get form data
    const formData = new FormData(this);
    const name = formData.get('name');
    const email = formData.get('email');
    const phone = formData.get('phone');
    const company = formData.get('company');
    const service = formData.get('service');
    const budget = formData.get('budget');
    const timeline = formData.get('timeline');
    const message = formData.get('message');
    const newsletter = formData.get('newsletter');

    // Validation
    if (!name || !email || !message) {
        showNotification('Please fill in all required fields.', 'error');
        return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showNotification('Please enter a valid email address.', 'error');
        return;
    }

    // Phone validation (if provided)
    if (phone && phone.length < 10) {
        showNotification('Please enter a valid phone number.', 'error');
        return;
    }

    // Simulate form submission
    const submitBtn = this.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnIcon = submitBtn.querySelector('.btn-icon');
    const originalText = btnText.textContent;

    btnText.textContent = 'Sending...';
    btnIcon.textContent = '⏳';
    submitBtn.disabled = true;

    // Simulate API call
    setTimeout(() => {
        showNotification('Thank you for your message! We\'ll get back to you within 24 hours.', 'success');
        this.reset();
        btnText.textContent = originalText;
        btnIcon.textContent = '→';
        submitBtn.disabled = false;

        // Log form data for demonstration
        console.log('Form submitted with data:', {
            name, email, phone, company, service, budget, timeline, message, newsletter
        });
    }, 2000);
});

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close">&times;</button>
    `;

    // Add to page
    document.body.appendChild(notification);

    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);

    // Auto hide after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);

    // Close button functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    });
}

// Schedule call button
document.querySelector('.schedule-btn').addEventListener('click', function() {
    showNotification('Redirecting to scheduling system...', 'info');
    // In a real application, this would open a calendar booking system
    setTimeout(() => {
        window.open('https://calendly.com', '_blank'); // Example scheduling service
    }, 1000);
});

// Form field enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Phone number formatting
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.startsWith('233')) {
                value = '+' + value;
            } else if (value.length > 0 && !value.startsWith('+')) {
                value = '+233' + value;
            }
            e.target.value = value;
        });
    }

    // Real-time email validation
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function(e) {
            const email = e.target.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (email && !emailRegex.test(email)) {
                e.target.style.borderColor = '#ef4444';
                showFieldError(e.target, 'Please enter a valid email address');
            } else {
                e.target.style.borderColor = '#374151';
                removeFieldError(e.target);
            }
        });
    }

    // Character counter for message field
    const messageField = document.getElementById('message');
    if (messageField) {
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.textContent = '0/500';
        messageField.parentNode.appendChild(counter);

        messageField.addEventListener('input', function(e) {
            const length = e.target.value.length;
            counter.textContent = `${length}/500`;

            if (length > 500) {
                counter.style.color = '#ef4444';
                e.target.style.borderColor = '#ef4444';
            } else {
                counter.style.color = '#6b7280';
                e.target.style.borderColor = '#374151';
            }
        });
    }

    // Form field focus effects
    const formInputs = document.querySelectorAll('#contactForm input, #contactForm textarea, #contactForm select');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentNode.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentNode.classList.remove('focused');
        });
    });
});

// Field error handling
function showFieldError(field, message) {
    removeFieldError(field);

    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function removeFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

// Get Started button functionality
document.querySelector('.get-started-btn').addEventListener('click', function() {
    document.querySelector('#contact').scrollIntoView({
        behavior: 'smooth'
    });
});

document.querySelector('.btn-primary').addEventListener('click', function() {
    document.querySelector('#contact').scrollIntoView({
        behavior: 'smooth'
    });
});

// CTA buttons functionality
document.querySelectorAll('.cta-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (this.textContent.includes('Start Your Project') || this.textContent.includes('Schedule a Call')) {
            document.querySelector('#contact').scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// View Templates button functionality
document.querySelector('.btn-secondary').addEventListener('click', function() {
    if (this.textContent.includes('View Templates')) {
        // In a real application, this would navigate to a templates page
        showNotification('Opening templates gallery...', 'info');
        setTimeout(() => {
            // For demo purposes, scroll to services section to show available services
            document.querySelector('#services').scrollIntoView({
                behavior: 'smooth'
            });
        }, 1000);
    }
});

// Navbar background on scroll
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(10, 10, 15, 0.98)';
    } else {
        navbar.style.background = 'rgba(10, 10, 15, 0.95)';
    }
});

// Add animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.querySelectorAll('.stat, .feature-card, .contact-item, .service-card, .testimonial-card, .portfolio-item, .tech-category').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Portfolio filtering functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');

            const filter = this.getAttribute('data-filter');

            portfolioItems.forEach(item => {
                const category = item.getAttribute('data-category');

                if (filter === 'all' || category.includes(filter)) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });

    // Portfolio CTA button
    const portfolioCTA = document.querySelector('.portfolio-cta .btn-secondary');
    if (portfolioCTA) {
        portfolioCTA.addEventListener('click', function() {
            showNotification('Opening full portfolio...', 'info');
            // In a real application, this would navigate to a full portfolio page
        });
    }

    // FAQ Accordion functionality
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', function() {
            const isActive = item.classList.contains('active');

            // Close all other FAQ items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });

            // Toggle current item
            if (isActive) {
                item.classList.remove('active');
            } else {
                item.classList.add('active');
            }
        });
    });
});

// Mobile menu functionality
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', function() {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', function() {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// Close mobile menu when clicking outside
document.addEventListener('click', function(e) {
    if (!hamburger.contains(e.target) && !navMenu.contains(e.target)) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }
});