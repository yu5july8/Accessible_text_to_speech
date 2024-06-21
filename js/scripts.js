$(document).ready(function() {
    // Sign Up and Log In Modals
    $('#signUpButton').on('click', function() {
        $('#signUpModal').show();
    });

    $('#logInButton').on('click', function() {
        $('#logInModal').show();
    });

    $('.close').on('click', function() {
        $('.modal').hide();
    });

    $(window).on('click', function(event) {
        if ($(event.target).hasClass('modal')) {
            $('.modal').hide();
        }
    });

    // Form Validation
    $('#signUpForm').on('submit', function(event) {
        let isValid = true;
        const email = $('#email').val();
        const password = $('#password').val();

        if (!validateEmail(email)) {
            isValid = false;
            $('#emailError').text('Invalid email format');
        } else {
            $('#emailError').text('');
        }

        if (!validatePassword(password)) {
            isValid = false;
            $('#passwordError').text('Password must be at least 8 characters long and include at least one number and one special character');
        } else {
            $('#passwordError').text('');
        }

        if (!isValid) {
            event.preventDefault();
        }
    });

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    function validatePassword(password) {
        const re = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        return re.test(String(password));
    }

    // File Upload
    $('#fileUpload').on('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const fileName = file.name;
            const fileSize = (file.size / 1024).toFixed(2) + ' KB';
            $('#filePreview').text(`File: ${fileName} (${fileSize})`);
        }
    });

    // Drag and Drop for File Upload
    let dropArea = $('#drop-area');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.on(eventName, preventDefaults);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.on(eventName, () => dropArea.addClass('highlight'));
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.on(eventName, () => dropArea.removeClass('highlight'));
    });

    // Handle dropped files
    dropArea.on('drop', handleDrop);

    function handleDrop(e) {
        let dt = e.originalEvent.dataTransfer;
        let files = dt.files;

        handleFiles(files);
    }

    function handleFiles(files) {
        ([...files]).forEach(uploadFile);
    }

    function uploadFile(file) {
        if (file) {
            const fileName = file.name;
            const fileSize = (file.size / 1024).toFixed(2) + ' KB';
            $('#filePreview').text(`File: ${fileName} (${fileSize})`);
        }
    }

    // Stripe Checkout
    $('#upgradeButton').on('click', function(event) {
        event.preventDefault();
        const stripe = Stripe('your_stripe_public_key');
        stripe.redirectToCheckout({
            sessionId: 'your_stripe_session_id'
        }).then(function(result) {
            if (result.error) {
                alert(result.error.message);
            }
        });
    });
});