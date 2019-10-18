function submitLogin() {
  const form = $('#login-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/login', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      window.location.href = '/home';
    }
  });
}
