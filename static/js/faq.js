document.addEventListener('DOMContentLoaded', function() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    const categoryButtons = document.querySelectorAll('.category-btn');
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('faqSearch');
    const noResults = document.getElementById('noResults');
    const faqCategories = document.querySelectorAll('.faq-category');
    
    // Toggle FAQ answers
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            this.classList.toggle('active');
            const answer = this.nextElementSibling;
            
            if (this.classList.contains('active')) {
                answer.style.maxHeight = answer.scrollHeight + 'px';
            } else {
                answer.style.maxHeight = 0;
            }
        });
    });
    
    // Filter by category
    categoryButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            const category = this.getAttribute('data-category');
            
            // Show/hide categories based on selection
            if (category === 'all') {
                faqCategories.forEach(cat => cat.style.display = 'block');
            } else {
                faqCategories.forEach(cat => {
                    if (cat.id === category) {
                        cat.style.display = 'block';
                    } else {
                        cat.style.display = 'none';
                    }
                });
            }
            
            // Reset search
            searchInput.value = '';
            noResults.style.display = 'none';
            
            // Reset question visibility
            faqQuestions.forEach(q => {
                q.parentElement.style.display = 'block';
                q.classList.remove('active');
                q.nextElementSibling.style.maxHeight = 0;
            });
        });
    });
    
    // Search functionality
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        let resultsFound = false;
        
        if (searchTerm.length < 2) {
            // Show all questions if search term is too short
            faqQuestions.forEach(q => q.parentElement.style.display = 'block');
            faqCategories.forEach(cat => cat.style.display = 'block');
            noResults.style.display = 'none';
            return;
        }
        
        // Set all category buttons to inactive except "All"
        categoryButtons.forEach(btn => {
            if (btn.getAttribute('data-category') === 'all') {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        // Show all categories
        faqCategories.forEach(cat => cat.style.display = 'block');
        
        // Filter questions
        faqQuestions.forEach(question => {
            const questionText = question.textContent.toLowerCase();
            const answerText = question.nextElementSibling.textContent.toLowerCase();
            
            if (questionText.includes(searchTerm) || answerText.includes(searchTerm)) {
                question.parentElement.style.display = 'block';
                resultsFound = true;
            } else {
                question.parentElement.style.display = 'none';
            }
        });
        
        // Check for empty categories
        faqCategories.forEach(category => {
            const visibleQuestions = category.querySelectorAll('.faq-item[style*="display: block"]');
            if (visibleQuestions.length === 0) {
                category.style.display = 'none';
            }
        });
        
        // Show no results message if needed
        noResults.style.display = resultsFound ? 'none' : 'block';
    }
    
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
});