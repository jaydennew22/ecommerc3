function sendOTP() {
    const email = document.getElementById('email').value.trim();
    const messageDiv = document.getElementById('message');
    messageDiv.innerText = '';

    if (!email) {
        messageDiv.innerText = 'Please enter your email.';
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        messageDiv.innerText = 'Please enter a valid email address.';
        return;
    }

    // Disable button to prevent multiple requests
    const button = document.querySelector('#step1 button');
    button.disabled = true;
    button.innerText = 'Sending...';

    fetch('/send-otp/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: 'email=' + encodeURIComponent(email)
    })
    .then(response => response.json())
    .then(data => {
        messageDiv.innerText = data.message || data.error;
        if (data.message) {
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
        }
    })
    .catch(error => {
        messageDiv.innerText = 'An error occurred. Please try again.';
        console.error('Error:', error);
    })
    .finally(() => {
        button.disabled = false;
        button.innerText = 'Send OTP';
    });
}

function resetPassword() {
    const email = document.getElementById('email').value.trim();
    const otp = document.getElementById('otp').value.trim();
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('message');
    messageDiv.innerText = '';

    if (!otp || otp.length !== 6 || !/^\d{6}$/.test(otp)) {
        messageDiv.innerText = 'Please enter a valid 6-digit OTP.';
        return;
    }

    if (!password || password.length < 6) {
        messageDiv.innerText = 'Password must be at least 6 characters long.';
        return;
    }

    // Disable button
    const button = document.querySelector('#step2 button');
    button.disabled = true;
    button.innerText = 'Resetting...';

    fetch('/reset-password/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: 'email=' + encodeURIComponent(email) + '&otp=' + encodeURIComponent(otp) + '&password=' + encodeURIComponent(password)
    })
    .then(response => response.json())
    .then(data => {
        messageDiv.innerText = data.message || data.error;
        if (data.message) {
            // redirect to login
            window.location.href = '/login/';
        }
    })
    .catch(error => {
        messageDiv.innerText = 'An error occurred. Please try again.';
        console.error('Error:', error);
    })
    .finally(() => {
        button.disabled = false;
        button.innerText = 'Reset Password';
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}