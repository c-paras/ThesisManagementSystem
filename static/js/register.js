function submit_register() {
    const email = document.getElementById('email');
    if(email.classList.contains('valid') === false) {
        console.log('Invalid email');
        return;
    }
    const pass = document.getElementById('password');
    const conf_pass = document.getElementById('confirm_password');
    if(pass.value !== conf_pass.value) {
        alert('Passwords don\'t match');
        return;
    }
    const request = new XMLHttpRequest();
    request.open('POST', '/register');
    request.onreadystatechange = function() {
        if(this.readyState === 4) {
            if(this.status === 200) {
                const res = JSON.parse(this.responseText);
                if(res.status === 'fail') {
                    alert('Error: ' + res.message);
                }
            } else {
                alert('Unexpected error occurred');
            }
        }
    };

    const form = document.getElementById('registration_form');
    request.send(new FormData(form));
}

function check_password() {
    const pass = document.getElementById('password');
    const conf_pass = document.getElementById('confirm_password');
    if(pass.value === conf_pass.value) {
        conf_pass.classList.remove('invalid');
        conf_pass.classList.add('valid');
    } else {
        conf_pass.classList.remove('valid');
        conf_pass.classList.add('invalid');
    }
}
