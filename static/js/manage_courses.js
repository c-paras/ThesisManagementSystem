function submitCO() {
    const form = $('#change-co');
    if (!formValid(form)) {
      return;
    }
    data = form.serializeArray()[0];

    makePOSTRequest('/manage_courses', data, (res) => {
      if (res.status === 'fail') {
        flash(res.message, error = true);
      } else {
        delayToast('Changes saved!', false);
        window.location.href = '/manage_courses';
      }
    });
}
  
  