function checkPassword() {
  const pass = $('#password');
  const confPass = $('#confirm-password');
  markFieldValid(confPass, pass.val() === confPass.val());
}

function submitRegister() {
  const form = $('#registration-form');
  checkPassword();
  if (!formValid(form)) {
    return;
  }
  makeRequest('/register', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      if (res.field) {
        markFieldValid($(`#${res.field}`), false);
      }
    } else {
      delayToast(
        'Account created!<br>You have been sent an activation email.',
        false
      );
      window.location.href = '/login';
    }
  });
}
