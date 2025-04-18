// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the current page highlight in navigation
    const currentLocation = window.location.href;
    const navLinks = document.querySelectorAll('header > .flex .desktop a');
    
    navLinks.forEach(link => {
        if (currentLocation === link.href) {
            link.classList.add('active');
        }
    });

});

document.getElementById('menu').addEventListener('click', () => {
    const menuBlock = document.getElementsByClassName('dropdown-content')[0]
    if (menuBlock.style.display === 'block') {
        menuBlock.style.display = 'none'
    } else {
        menuBlock.style.display = 'block'
    }
})