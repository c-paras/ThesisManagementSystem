function submitCreate() {
  const form = $('#create-topic-form');
  if (!formValid(form)) {
    return;
  }

  makeRequest('/create_topic', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Topic created!', false);
      window.location.href = '/home';
    }
  });
}




