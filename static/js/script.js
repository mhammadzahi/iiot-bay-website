// Email validation helper function
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}


// Newsletter form handler
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.getElementById('newsletter-form');
    const newsletterSubmit = document.getElementById('newsletter-submit');
    
    if (newsletterForm && newsletterSubmit) {
        newsletterSubmit.addEventListener('click', function(e) {
            e.preventDefault();
            
            const emailInput = newsletterForm.querySelector('input[name="email"]');
            const email = emailInput.value.trim();
            
            // Validate email
            if (!email) {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'error',
                    title: 'Please enter your email address',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: false
                });
                return;
            }
            
            if (!isValidEmail(email)) {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'error',
                    title: 'Please enter a valid email address',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: false
                });
                return;
            }
            
            // Disable button and show loading state
            newsletterSubmit.disabled = true;
            const originalContent = newsletterSubmit.innerHTML;
            newsletterSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // Submit to backend
            fetch('/api/newsletter/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json())
            .then(data => {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'success',
                    title: 'Subscribed successfully!',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true
                });
                newsletterForm.reset();
            })
            .catch(error => {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'error',
                    title: error.message || 'Something went wrong',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true
                });
            })
            .finally(() => {
                newsletterSubmit.disabled = false;
                newsletterSubmit.innerHTML = originalContent;
            });
        });
        
        // Also handle form submit event
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            newsletterSubmit.click();
        });
    }
});


// Contact form handler
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contact-form');
    const contactSubmit = document.getElementById('contact-submit');
    
    if (contactForm && contactSubmit) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(contactForm);
            const name = formData.get('name').trim();
            const email = formData.get('email').trim();
            const subject = formData.get('subject').trim();
            const message = formData.get('message').trim();
            
            // Get Turnstile token
            const turnstileResponse = document.querySelector('[name="cf-turnstile-response"]');
            const turnstileToken = turnstileResponse ? turnstileResponse.value : '';
            
            // Validate form
            if (!name || !email || !message) {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'error',
                    title: 'Please fill in all required fields',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true
                });
                return;
            }
            
            if (!isValidEmail(email)) {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'error',
                    title: 'Please enter a valid email address',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true
                });
                return;
            }
            
            if (!turnstileToken) {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'error',
                    title: 'Please wait for security verification to complete',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true
                });
                return;
            }
            
            // Disable button and show loading state
            contactSubmit.disabled = true;
            const originalContent = contactSubmit.innerHTML;
            contactSubmit.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Sending...';
            
            // Get current page URL to extract language
            const currentPath = window.location.pathname;
            const contactUrl = currentPath; // Use current URL which includes language prefix
            
            // Submit form as JSON
            fetch(contactUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    subject: subject,
                    message: message,
                    'cf-turnstile-response': turnstileToken
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        toast: true,
                        position: 'top-end',
                        icon: 'success',
                        title: 'Message sent successfully!',
                        showConfirmButton: false,
                        timer: 3000,
                        timerProgressBar: true
                    });
                    contactForm.reset();
                    // Reset Turnstile widget
                    if (typeof turnstile !== 'undefined') {
                        turnstile.reset();
                    }
                    // Redirect to services page after showing success message
                    setTimeout(() => {
                        window.location.href = '/services';
                    }, 2000);
                    
                } else {
                    throw new Error(data.message || 'Failed to send message');
                }
            })
            .catch(error => {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'error',
                    title: error.message || 'Something went wrong',
                    showConfirmButton: false,
                    timer: 3000,
                    timerProgressBar: true
                });
            })
            .finally(() => {
                contactSubmit.disabled = false;
                contactSubmit.innerHTML = originalContent;
            });
        });
    }
});
