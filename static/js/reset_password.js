function submitResetReq() {
  const form = $('#resetPasswordReq-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/reset_password_req', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('You have been sent an email with instructions!', false);
      window.location.href = '/login';
    }
  });
}

function submitReset(user_id, reset_id) {
  const form = $('#resetPassword-form');
  if (!formValid(form)) {
    return;
  }
  const data = {
    'user_id': user_id,
    'reset_id': reset_id,
    'new_pass': $('#new-password').val(),
    'new_confirm': $('#new-confirm-password').val()
  };
  makePOSTRequest('/reset_password', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      if (res.field) {
        markFieldValid($(`#${res.field}`), false);
      }
    } else {
      delayToast('Password changed!', false);
      window.location.href = '/login';
    }
  });
}

$(document).ready(function(){
  $('#resetPasswordReq-modal').modal();
});
