function addMaterial() {
  const form = $('#add-material-form');
  if (!formValid(form)) {
    return;
  }
  $('#btn-request').toggle();
  $('#btn-cancel').toggle();
  $('#upload-spinner').toggle();
  makeMultiPartRequest('/upload_material', form, (res) => {
    $('#btn-request').toggle();
    $('#btn-cancel').toggle();
    $('#upload-spinner').toggle();
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Material added to course!', error = false);
      window.location.href = '/manage_courses';
    }
  });
}
