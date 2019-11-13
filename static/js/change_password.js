function submitChange() {
  const form = $('#changePassword-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/change_password', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast(
        'Password Changed!',false);
      window.location.href = '/home';
    }
  });
}

function submitResetReq() {
  const form = $('#resetPasswordReq-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/reset_password_req', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
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
    'new_pass': $('#new-password').val()
  };
  makePOSTRequest('/reset_password', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Password Changed!', false);
      window.location.href = '/login';
    }
  });
}

function checkPassword() {
  const pass = $('#new-password');
  const confPass = $('#new-confirm-password');
  markFieldValid(confPass, pass.val() === confPass.val());
}

$(document).ready(function(){
  $('#resetPasswordReq-modal').modal();
  $('#changePassword-modal').modal();
});