function submitRegister() {
  let invalid = false;
  $('#registration-form').find('input').each(function () {
    if ($(this).val() === '') {
      invalid = true;
    }
  });
  if (invalid || $('#registration-form').find('.invalid').length) {
    return;
  }

  const form = $('#registration-form');

  fetch('/register', {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    },
    method: 'POST',
    body: form.serialize()
  })
  .then(res => res.json())
  .then(res => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      flash('Account created!', error = false);
    }
  });
}

function checkPassword() {
  const pass = $('#password');
  const confPass = $('#confirm-password');
  if (pass.val() === confPass.val()) {
    confPass.removeClass('invalid');
    confPass.addClass('valid');
  } else {
    confPass.removeClass('valid');
    confPass.addClass('invalid');
  }
}

function checkKey() {
  const field = $('#registration-key');
  if (field.val() !== '') {
    field.removeClass('invalid');
    field.addClass('valid');
  } else {
    field.removeClass('valid');
    field.addClass('invalid');
  }
}
