function submitRegister() {
    const email = $('#email');
    if(email.val().indexOf('@') < 0) {
        alert('Please enter valid email');
        return;
    }
    const pass = $('#password');
    const confPass = $('#confirm-password');
    if(pass.val() !== confPass.val()) {
        alert('Passwords don\'t match');
        return;
    }

    const form = $('#registration-form');

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

function checkPassword() {
    const pass = $('#password');
    const confPass = $('#confirm-password');
    if(pass.val() === confPass.val()) {
        confPass.removeClass('invalid');
        confPass.addClass('valid');
    } else {
        confPass.removeClass('valid');
        confPass.addClass('invalid');
    }
}
