function submitCO() {
  const form = $('#change-co');
  if (!formValid(form)) {
    return;
  }
  data = form.serializeArray();
  makePOSTRequest('/update_course_offering', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Details loaded', false);
      window.location.href = '/manage_courses';
    }
  });
}

function setSessions() {
  course = $('#courses').children("option:selected").val();
  makePOSTRequest('/get_sessions', course, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      //delayToast('Details loaded', false);
      //window.location.href = '/manage_courses';
      $('#sessions option').each(function() {
        $(this).remove();
      });
      $.each(res.data, function(index, val) {
        $('#sessions').append($('<option>', {
          value: val[1],
          text: val[0]
        }));
      });
      $('select').formSelect();
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
  let text = 'Are you sure you want to delete the task: ' + taskName;
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
  let text = 'Are you sure you want to delete the Material: ' + materialName;
  $('#deletion-message').text(text);
  $('#confirm-deletion').click(function callDelet() {
    deleteMaterial(materialId);
  });
  $('#deleteModal').modal('open');
}

$(document).ready(function(){
  $('.modal').modal();
});

