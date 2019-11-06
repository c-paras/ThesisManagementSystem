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

function makeChange(data, type, checkbox_id){
  makePOSTRequest('/manage_courses', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      if( type === '0' ){
        $(checkbox_id).prop('checked', true);
      } else {
        $(checkbox_id).prop('checked', false);
      }
    } else {
      if( type === '1' ){
        flash('Item is now visible to students', false);
        $(checkbox_id).attr("data-totype", "0");
        $(checkbox_id).prop('checked', true);
      }else{
        flash('Students can no longer view the item', false);
        $(checkbox_id).attr("data-totype", "1");
        $(checkbox_id).prop('checked', false);
      }
    }
  });
}

function updateMat(mat_id, checkbox_id) {

  type = $(checkbox_id).attr("data-totype");
  data = {'table': 'materials', 'id': mat_id, 'type': type};
  
  makeChange(data, type, checkbox_id);
}

function updateTask(task_id, checkbox_id) {

  type = $(checkbox_id).attr("data-totype");
  data = {'table': 'tasks', 'id': task_id, 'type': type};

  makeChange(data, type, checkbox_id);
}
