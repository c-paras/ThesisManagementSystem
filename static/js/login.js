function submitLogin() {
  const form = $('#login-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/login', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      if (res.field) {
        markFieldValid($(`#${res.field}`), false);
      }
    } else {
      window.location.href = '/home';
    }
  });
}
