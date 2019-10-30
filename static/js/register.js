function submitRegister() {
  const form = $('#registration-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/register', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast(
        'Account created!<br>You have been sent an activation email.',
        false
      );
      window.location.href = '/login';
    }
  });
}

function checkPassword() {
  const pass = $('#password');
  const confPass = $('#confirm-password');
  markFieldValid(confPass, pass.val() === confPass.val());
}

function checkKey() {
  const key = $('#registration-key');
  markFieldValid(key, key.val() !== '');
}
