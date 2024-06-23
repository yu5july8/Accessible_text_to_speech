document.addEventListener('DOMContentLoaded', function() {
    // Stripe public key
    const stripePublicKey = document.getElementById('stripe-public-key').getAttribute('data-key');
    const stripe = Stripe(stripePublicKey);

    // Event listener for subscription button
    const checkoutButton = document.getElementById('checkout-button');
    if (checkoutButton) {
        checkoutButton.addEventListener('click', function () {
            fetch('/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (sessionId) {
                return stripe.redirectToCheckout({ sessionId: sessionId });
            })
            .then(function (result) {
                if (result.error) {
                    alert(result.error.message);
                }
            })
            .catch(function (error) {
                console.error('Error:', error);
            });
        });
    }
});