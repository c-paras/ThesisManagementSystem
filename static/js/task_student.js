function uploadFile() {
  const form = $('#file-upload-form');
  if ($('#file-name').val() === '') {
    flash('Please specify a file', true);
    return;
  }
  if ($('#all-own-work').prop('checked') !== true) {
    flash('You must certify this is all your own work', true);
    return;
  }
  $('#upload-spinner').toggle();
  $('#submit-btn').toggle();
  makeMultiPartRequest('/submit_file_task', form, (res) => {
    $('#upload-spinner').toggle();
    $('#submit-btn').toggle();
    if (res.status === 'fail') {
      flash(res.message, true);
      return;
    }
    flash("Success");
  });
}

$(function () {
  $('#all-own-work').change(function () {
    if ($('#all-own-work').prop('checked')) {
      $('#all-own-work').val('true');
    } else {
      $('#all-own-work').val('true');
    }
  });
});
