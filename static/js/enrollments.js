
function addStaff() {
  const form = $('#enroll-email-form');
  if (!formValid(form)) {
    return;
  }
  data = form.serializeArray();
  let form_dict = {
    account_type: data[0].value,
    email: data[1].value,
    name: data[2].value,
    table: data[3].value
  };
  makePOSTRequest('/add_staff', form_dict, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Account type changed', false);
      window.location.href = location.href.replace('#!', '');
    }
  });
}

function enrollUser() {
  const form = $('#enroll-email-form');
  if (!formValid(form)) {
    return;
  }
  data = form.serializeArray();
  let form_dict = {
    account_type: data[0].value,
    email: data[1].value,
    name: data[2].value,
    table: data[3].value
  };
  makePOSTRequest('/enrol_user', form_dict, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('User enrolled', false);
      window.location.href = '/manage_courses';
    }
  });
}
  
function enrollFile() {
  const form = $('#enroll-file-form');
  if (!formValid(form)) {
    return;
  }
  $('#btn-request-enroll').toggle();
  $('#btn-cancel-enroll').toggle();
  $('#upload-spinner-enroll').toggle();
  makeMultiPartRequest('/upload_enrollments', form, (res) => {
    $('#btn-request-enroll').toggle();
    $('#btn-cancel-enroll').toggle();
    $('#upload-spinner-enroll').toggle();
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Users enrolled', false);
      window.location.href = '/manage_courses';
    }
});
}

function addStaffFile() {
  const form = $('#enroll-file-form');
  if (!formValid(form)) {
    return;
  }
  $('#btn-request-enroll').toggle();
  $('#btn-cancel-enroll').toggle();
  $('#upload-spinner-enroll').toggle();
  makeMultiPartRequest('/upload_staff', form, (res) => {
    $('#btn-request-enroll').toggle();
    $('#btn-cancel-enroll').toggle();
    $('#upload-spinner-enroll').toggle();
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Account type changed', false);
      window.location.href = location.href.replace('#!', '');
    }
  });
}
  
function toggleEnrollTypeCourse() {
  if ($('#email-type').prop('checked') === true) {
    $('#enroll-user-block').show();
    $('#enroll-file-block').hide();
    $('#btn-request-enroll').attr('onclick', 'enrollUser()');
  } else {
    $('#enroll-user-block').hide();
    $('#enroll-file-block').show();
    $('#btn-request-enroll').attr('onclick', 'enrollFile()');
  }
}
  
function toggleEnrollTypeStaff() {
  if ($('#email-type').prop('checked') === true) {
    $('#enroll-user-block').show();
    $('#enroll-file-block').hide();
    $('#btn-request-enroll').attr('onclick', 'addStaff()');
  } else {
    $('#enroll-user-block').hide();
    $('#enroll-file-block').show();
    $('#btn-request-enroll').attr('onclick', 'addStaffFile()');
  }
}

function setFormTypeAddStaff() {
  $('#account_type_enroll option').each(function() {
    $(this).remove();
  });
  $('#account_type_enroll').append('<option value="-1" disabled selected>Account type</option>');
  $('#account_type_enroll').append('<option value="supervisor" selected="selected">Staff</option>');
  $('#btn-request-enroll').attr('onclick', 'addStaff()');
  $('#enroll-title').text("Add Staff");
  $('#select-e-type').text("Select staff type");
  $('[name="enroll-type"]').change(function () {
   toggleEnrollTypeStaff();
  });
  $('#enroll-account-modal').modal('open');
  $('select').formSelect();
}

function setFormTypeUser() {
  $('#account_type_enroll option').each(function() {
    $(this).remove();
  });
  $('#account_type_enroll').append('<option value="-1" disabled selected>Course role</option>');
  $('#account_type_enroll').append('<option value="student" selected="selected">Student</option>');
  //$('#account_type_enroll').append('<option value="course_admin">Admin</option>');
  $('#btn-request-enroll').attr('onclick', 'enrollUser()');
  $('#enroll-title').text("Enroll Users");
  $('#select-e-type').text("Select enrollment type");
  $('[name="enroll-type"]').change(function () {
    toggleEnrollTypeCourse();
  });
  $('select').formSelect();
}
