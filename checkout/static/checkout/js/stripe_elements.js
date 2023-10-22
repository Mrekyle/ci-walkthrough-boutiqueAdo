
// Getting the stripe element ID's and removing the '' from the beginning and the end 
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);

// Creating an instance of the stripe payment wall
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

// Adding style to the card input inside of the js file 
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4',
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

// Creating the card element itself and adding in the defined styles from above
var card = elements.create('card', {style: style});
card.mount('#card-element');

// Detecting a change on the element to display the error message that was given by the stripe payment features

card.addEventListener('change', function(event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `
        $(errorDiv).html(html);
        } else {
            errorDiv.textContent = '';
        }
});

// Handling the payment form submission

var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    // Preventing the forms default submit behavior. To allow for stripe to run its validation
    ev.preventDefault();

    // Disabling the submit button and card element whilst everything is being validated
    // to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true)
    
    // Stripes validation functions 
    stripe.confirmCardPayment(clientSecret,  {
        payment_method: {
            card: card,
            }
    }).then(function(result) {
        if(result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>
                `
                $(errorDiv).html(html);
            // Logging out the error for development debugging
            console.log(result.error.message)
            // If there is an error. Re enable the card element and submit buttons for the user to fix the problem 
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false)
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.onsubmit()
                // Logging out the success message for development purposes
                console.log('Success')
            }
        }
    })
})