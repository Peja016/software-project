document.addEventListener('DOMContentLoaded', () => {
    const testimonials = document.querySelectorAll('.testimonial');
    let currentIndex = 0;
    
    testimonials.forEach((testimonial, index) => {
        if (index !== 0) {
            testimonial.style.opacity = 0;
            testimonial.style.visibility = 'hidden';
        }
    });

    const showNextTestimonial = () => {
        testimonials[currentIndex].style.opacity = 0;
        testimonials[currentIndex].style.visibility = 'hidden';
        
        currentIndex = (currentIndex + 1) % testimonials.length;
        
        testimonials[currentIndex].style.opacity = 1;
        testimonials[currentIndex].style.visibility = 'visible';
    }

    setInterval(showNextTestimonial, 6000);
});