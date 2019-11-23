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

function openAddMaterial() {
  $('#add-material-modal-heading').html('Add Material');
  $('#old-material-id').val('None');
  $('#file-label').val('');
  $('#btn-request').html('Upload');

  $('#upload-file-area').show();
  $('#old-file-area').hide();

  $('#add-material-modal').modal('open');
}

function deleteOldFile(){
  $('#upload-file-area').show();
  $('#old-file-area').hide();

  $('#delete-old-file').val('true');
}

function openEditMaterial(materialID, materialName, filePath, fileName) {
  $('#add-material-modal-heading').html('Edit Material');
  $('#old-material-id').val(materialID);
  $('#file-label').val(materialName);

  $('#old-file-name').html(fileName);
  $('#old-file-download').attr("href", filePath);

  $('#upload-file-area').hide();
  $('#old-file-area').show();

  $('#delete-old-file').val('false');

  $('#btn-request').html('Confirm');
  $('#add-material-modal').modal('open');
}
