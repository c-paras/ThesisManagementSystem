function toggleSubmissionType() {
  if ($('#text-type').prop('checked') === true) {
    $('#text-entry-block').show();
    $('#file-upload-block').hide();
  } else {
    $('#text-entry-block').hide();
    $('#file-upload-block').show();
  }
}

$('[name="submission-type"]').change(function () {
  toggleSubmissionType();
});

toggleSubmissionType();
