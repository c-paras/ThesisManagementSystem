function submitCO() {
  const form = $('#change-co');
  if (!formValid(form)) {
    return;
  }
  const data = form.serializeArray()[0];

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
  const type = $(checkbox_id).attr('data-totype');
  const data = {'table': 'materials', 'id': mat_id, 'type': type};
  makeChange(data, type, checkbox_id);
}

function updateTask(task_id, checkbox_id) {
  const type = $(checkbox_id).attr('data-totype');
  const data = {'table': 'tasks', 'id': task_id, 'type': type};
  makeChange(data, type, checkbox_id);
}

function exportMarks(enrolledStudents, tasks) {
  const data = {
    'studentIds': enrolledStudents,
    'taskIds': tasks
  };
  
  makePOSTRequest('/export_marks', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      /* let csv = 'Name,zID,Task Name,Assessor Mark,Supervisor Mark,Assessor,Supervisor\n'; */
      let csv = 'zID,Name,Task Name,Supervisor,Assessor,Supervisor Mark,Assessor Mark\n';

      res.details.forEach(entry => {
        entry.splice(5, 3);
        const dat = [entry[1]].concat([entry[0]]).concat([entry[2]]).concat(entry.splice(3).reverse());
        csv += `${dat.join(',')}\n`;
      });

      const hiddenElement = document.getElementById('dummyDownload');
      hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);
      hiddenElement.target = '_blank';
      hiddenElement.download = 'marks.csv';
      hiddenElement.click();
    }
  });

}

function deleteTask(taskId) {
  const data = {
    "taskId": taskId
  };

  makePOSTRequest('/delete_task', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast(res.message);
      location.reload();
    }
  });
}

function deleteMaterial(materialId) {
  const data = {
    "materialId": materialId
  };

  makePOSTRequest('/delete_material', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast(res.message);
      location.reload();
    }
  });
}

function openTaskDeleteConfirmation(taskName, taskId) {
  const text = 'Are you sure you want to delete the task: ' + taskName;
  $('#deletion-message').text(text);
  $('#confirm-deletion').click(function callDelet() {
    deleteTask(taskId);
  });
  $('#deleteModal').modal('open');
}

function checkDeleteTask(taskName, taskId) {
  const data = {
    "taskId": taskId
  };

  makePOSTRequest('/check_delete_task', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      openTaskDeleteConfirmation(taskName, taskId);
    }
  });
}

function openMaterialDeleteConfirmation(materialName, materialId) {
  const text = 'Are you sure you want to delete the Material: ' + materialName;
  $('#deletion-message').text(text);
  $('#confirm-deletion').click(function callDelet() {
    deleteMaterial(materialId);
  });
  $('#deleteModal').modal('open');
}

$(document).ready(function(){
  $('.modal').modal();
});
