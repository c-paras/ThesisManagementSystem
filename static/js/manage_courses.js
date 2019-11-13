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
      delayToast('Details loaded', false);
      window.location.href = '/manage_courses';
    }
  });
}

function makeChange(data, type, checkbox_id) {
  makePOSTRequest('/manage_courses', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      if (type === '0') {
        $(checkbox_id).prop('checked', true);
      } else {
        $(checkbox_id).prop('checked', false);
      }
    } else {
      if (type === '1') {
        flash('Item is now visible to students', false);
        $(checkbox_id).attr('data-totype', '0');
        $(checkbox_id).prop('checked', true);
      } else {
        flash('Students can no longer view the item', false);
        $(checkbox_id).attr('data-totype', '1');
        $(checkbox_id).prop('checked', false);
      }
    }
  });
}

function updateMat(mat_id, checkbox_id) {
  type = $(checkbox_id).attr('data-totype');
  data = {'table': 'materials', 'id': mat_id, 'type': type};
  makeChange(data, type, checkbox_id);
}

function updateTask(task_id, checkbox_id) {
  type = $(checkbox_id).attr('data-totype');
  data = {'table': 'tasks', 'id': task_id, 'type': type};
  makeChange(data, type, checkbox_id);
}

function enrollUser() {
  const form = $('#enroll-email-form');
  if (!formValid(form)) {
    return;
  }
  data = form.serializeArray();
  var form_dict = {
    account_type: data[0].value,
    email: data[1].value,
    name: data[2].value,
    table: data[3].value
  };
  makePOSTRequest('/manage_courses', form_dict, (res) => {
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
  console.log(form);
  if (!formValid(form)) {
    return;
  }
  data = form.serializeArray();
  var form_dict = {
    files: form,
    table: data[1].value,
    file_name: data[0].value
  };
  console.log(form_dict);
  //$('#btn-request-enroll').toggle();
  //$('#btn-cancel-enroll').toggle();
  //$('#upload-spinner-enroll').toggle();
  makeMultiPartRequest('/upload_enrollments', form, (res) => {
    $('#btn-request-enroll').toggle();
    $('#btn-cancel-enroll').toggle();
    $('#upload-spinner-enroll').toggle();
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('User enrolled', false);
      window.location.href = '/manage_courses';
    }
  });
}

function toggleEnrollType() {
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

$('[name="enroll-type"]').change(function () {
  toggleEnrollType();
});
