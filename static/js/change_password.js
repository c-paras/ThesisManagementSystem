function submitChange() {
  const form = $('#changePassword-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/change_password', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      if (res.field) {
        markFieldValid($(`#${res.field}`), false);
      }
    } else {
      delayToast('Password changed!',false);
      location.reload();
    }
  });
}

function checkPassword() {
  const pass = $('#new-password');
  const confPass = $('#new-confirm-password');
  markFieldValid(confPass, pass.val() === confPass.val());
}

$(document).ready(function(){
  $('#changePassword-modal').modal();
});
