function submit_register() {
    const email = $('#email');
    if(email.val().indexOf('@') < 0) {
        alert('Please enter valid email');
        return;
    }
    const pass = $('#password');
    const conf_pass = $('#confirm_password');
    if(pass.val() !== conf_pass.val()) {
        alert('Passwords don\'t match');
        return;
    }

    const form = $('#registration_form');

    fetch('/register', {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
        },
        method: 'POST',
        body: form.serialize()
    })
        .then(res => res.json())
        .then(res => {
            if(res.status === 'fail') {
                alert('Error: ' + res.message);
            } else {
                alert('Success');
            }
        });
}

function check_password() {
    const pass = $('#password');
    const conf_pass = $('#confirm_password');
    if(pass.val() === conf_pass.val()) {
        conf_pass.removeClass('invalid');
        conf_pass.addClass('valid');
    } else {
        conf_pass.removeClass('valid');
        conf_pass.addClass('invalid');
    }
}
