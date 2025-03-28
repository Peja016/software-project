// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-nav');
    
    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', function() {
            mainNav.classList.toggle('show');
            this.classList.toggle('active');
        });
    }
    
    // Modal functionality
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const closeBtns = document.querySelectorAll('.close');
    const showRegisterForm = document.getElementById('showRegisterForm');
    const showLoginForm = document.getElementById('showLoginForm');
    
    // Open login modal
    if (loginBtn && loginModal) {
        loginBtn.addEventListener('click', function() {
            loginModal.style.display = 'block';
        });
    }
    
    // Open register modal
    if (registerBtn && registerModal) {
        registerBtn.addEventListener('click', function() {
            registerModal.style.display = 'block';
        });
    }
    
    // Close modals when clicking the X
    if (closeBtns) {
        closeBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                if (loginModal) loginModal.style.display = 'none';
                if (registerModal) registerModal.style.display = 'none';
            });
        });
    }
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === loginModal) {
            loginModal.style.display = 'none';
        }
        if (event.target === registerModal) {
            registerModal.style.display = 'none';
        }
    });
    
    // Switch between login and register forms
    if (showRegisterForm) {
        showRegisterForm.addEventListener('click', function(e) {
            e.preventDefault();
            if (loginModal) loginModal.style.display = 'none';
            if (registerModal) registerModal.style.display = 'block';
        });
    }
    
    if (showLoginForm) {
        showLoginForm.addEventListener('click', function(e) {
            e.preventDefault();
            if (registerModal) registerModal.style.display = 'none';
            if (loginModal) loginModal.style.display = 'block';
        });
    }
    
    // Form submission handling
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Get form data
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Here you would typically send this data to your server
            console.log('Login attempt:', { email, password });
            
            // For demo purposes, show success message
            alert('Login successful! (Demo only)');
            loginModal.style.display = 'none';
        });
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Get form data
            const fullName = document.getElementById('fullName').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            // Basic validation
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            
            // Here you would typically send this data to your server
            console.log('Registration attempt:', { fullName, email, password });
            
            // For demo purposes, show success message
            alert('Registration successful! (Demo only)');
            registerModal.style.display = 'none';
        });
    }
    
    // Modified testimonial slider functionality - Fixed to prevent auto-scrolling
    const testimonials = document.querySelector('.testimonial-slider');
    if (testimonials) {
        const testimonialItems = document.querySelectorAll('.testimonial');
        let currentIndex = 0;
        let autoRotateInterval = null;
        
        if (testimonialItems.length > 1) {
            // Position testimonials for absolute positioning
            testimonials.style.position = 'relative';
            testimonials.style.minHeight = '250px';
            
            testimonialItems.forEach((item, index) => {
                item.style.position = 'absolute';
                item.style.top = '0';
                item.style.left = '0';
                item.style.width = '100%';
                item.style.transition = 'opacity 0.8s ease-in-out';
                
                if (index === 0) {
                    item.style.opacity = '1';
                    item.style.zIndex = '1';
                } else {
                    item.style.opacity = '0';
                    item.style.zIndex = '0';
                }
            });
            
            // Function to rotate testimonials without scrolling the page
            const rotateTestimonials = () => {
                // Hide current testimonial
                testimonialItems[currentIndex].style.opacity = '0';
                testimonialItems[currentIndex].style.zIndex = '0';
                
                // Increment to next testimonial
                currentIndex = (currentIndex + 1) % testimonialItems.length;
                
                // Show next testimonial
                testimonialItems[currentIndex].style.opacity = '1';
                testimonialItems[currentIndex].style.zIndex = '1';
            };
            
            // Start auto-rotation with 8 second interval
            autoRotateInterval = setInterval(rotateTestimonials, 2000);
            
            // Pause on mouse enter
            testimonials.addEventListener('mouseenter', () => {
                clearInterval(autoRotateInterval);
            });
            
            // Resume on mouse leave
            testimonials.addEventListener('mouseleave', () => {
                autoRotateInterval = setInterval(rotateTestimonials, 8000);
            });
        }
    }
    
    // Initialize the current page highlight in navigation
    const currentLocation = window.location.href;
    const navLinks = document.querySelectorAll('.main-nav a');
    
    navLinks.forEach(link => {
        if (currentLocation.includes(link.href)) {
            link.classList.add('active');
        }
    });
    
    // Contact form submission
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const name = document.getElementById('contactName').value;
            const email = document.getElementById('contactEmail').value;
            const subject = document.getElementById('contactSubject').value;
            const message = document.getElementById('contactMessage').value;
            
            // Here you would typically send this data to your server
            console.log('Contact form submission:', { name, email, subject, message });
            
            // For demo purposes, show success message
            alert('Message sent successfully! (Demo only)');
            contactForm.reset();
        });
    }
    
    // Booking functionality for bikes
    const bookButtons = document.querySelectorAll('.book-btn');
    
    if (bookButtons) {
        bookButtons.forEach(button => {
            button.addEventListener('click', function() {
                const bikeId = this.getAttribute('data-bike-id');
                const bikeName = this.getAttribute('data-bike-name');
                
                // In a real application, you would store this in session/local storage
                // or send directly to a server
                console.log(`Booking bike: ${bikeName} (ID: ${bikeId})`);
                
                // For demo purposes
                alert(`You've selected the ${bikeName}. Proceed to payment.`);
                
                // Redirect to payment page or show payment modal
                // window.location.href = `pay.html?bike=${bikeId}`;
            });
        });
    }
    
    // Payment processing (simplified demo)
    const paymentForm = document.getElementById('paymentForm');
    
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get payment details
            const cardName = document.getElementById('cardName').value;
            const cardNumber = document.getElementById('cardNumber').value;
            const expiryDate = document.getElementById('expiryDate').value;
            const cvv = document.getElementById('cvv').value;
            
            // Validate card number (simplified)
            if (cardNumber.length < 16) {
                alert('Please enter a valid card number');
                return;
            }
            
            // Here you would process payment through a payment gateway
            console.log('Processing payment:', { cardName, cardNumber, expiryDate, cvv });
            
            // For demo purposes
            alert('Payment successful! Your bike is ready for pickup. (Demo only)');
            paymentForm.reset();
        });
    }
});