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

function updateMat(mat_id, checkbox_id) {

  type = $(checkbox_id).attr("data-totype");
  data = {'table': 'materials', 'id': mat_id, 'type': type};

  makePOSTRequest('/manage_courses', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      if( type === 0 ){
        $(checkbox_id).prop('checked', true);
      } else {
        $(checkbox_id).prop('checked', false);
      }
    } else {
      flash('Visibility changed', false);
      if( type === 1 ){
        $(checkbox_id).attr("data-totype", "0");
      }else{
        $(checkbox_id).attr("data-totype", "1");
      }
    }
  });
}

function updateTask(task_id, checkbox_id) {

  type = $(checkbox_id).attr("data-totype");
  data = {'table': 'tasks', 'id': task_id, 'type': type};

  makePOSTRequest('/manage_courses', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      if( type === 0 ){
        $(checkbox_id).prop('checked', true);
      } else {
        $(checkbox_id).prop('checked', false);
      }
    } else {
      flash('Visibility changed', false);
      if( type === 1 ){
        $(checkbox_id).attr("data-totype", "0");
      }else{
        $(checkbox_id).attr("data-totype", "1");
      }
    }
  });
}