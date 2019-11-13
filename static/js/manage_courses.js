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

function exportMarks(enrolledStudents, tasks) {

  data = {
    'studentIds': enrolledStudents,
    'taskIds': tasks
  };
  
  makePOSTRequest('/export_marks', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      let csv = 'Name,zID,Task Name,Assessor Mark,Supervisor Mark,Assessor,Supervisor\n';

      res.details.forEach(element => {
        csv += element[0] + ',';
        csv += element[1] + ',';
        csv += element[2] + ',';
        csv += element[3] + ',';
        csv += element[4] + ',';
        csv += element[8] + ',';
        csv += element[9] + '\n';
      });

      let hiddenElement = document.getElementById('dummyDownload');
      hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
      hiddenElement.target = '_blank';
      hiddenElement.download = 'marks.csv';
      hiddenElement.click();
    }
  });

}
