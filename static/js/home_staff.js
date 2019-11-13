function toggleViewAssessor() {
  if ($('#reject-check').prop('checked') === true) {
    $('#assessor-view').hide();
  } else {
    $('#assessor-view').show();
  }
}

function openRequestModal(studentId, topicId) {
  const data = {
    'student_id': studentId,
    'topic_id': topicId
  };

  makePOSTRequest('/lookup_request', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      return;
    }
    if (res.reqStatus !== 'pending') {
      flash('Topic unavailable to accept or reject');
      return;
    }
    const form = $('#respond-form');
    form.children('input[name="topic"]').val(topicId);
    form.children('input[name="student-id"]').val(studentId);
    $('#accept-check').prop('checked', true);
    $('#reject-check').prop('checked', false);
    $('#student-name').html(`
      ${res.userName} <a href="mailto:${res.email}">(${res.email.split('@')[0]})</a>
    `);
    $('#topic-name').text(res.topicName);

    const d = new Date(res.reqDate);
    let dif = new Date(new Date() - d)/1000;
    let timeframe =" Seconds Ago";

    if (dif > 60){
      dif /= 60;
      timeframe = " Minutes Ago";
    }

    if(dif > 60){
      dif = dif/60;
      timeframe = " Hours Ago";
    }

    if(dif > 24 && timeframe === " Hours Ago"){
      dif /= 24;
      timeframe = " Days Ago";
    }
    dif = Math.floor(dif);
    const date = d.getDate();
    const year = d.getFullYear();
    let month = [];
    month[0] = "Jan";
    month[1] = "Feb";
    month[2] = "Mar";
    month[3] = "Apr";
    month[4] = "May";
    month[5] = "Jun";
    month[6] = "Jul";
    month[7] = "Aug";
    month[8] = "Sep";
    month[9] = "Oct";
    month[10] = "Nov";
    month[11] = "Dec";
    month_code = month[d.getMonth()];
    const date_string = (date + ' ' + month_code + ' ' + year);
    $('#date-requested').attr('data-tooltip', date_string);
    $('#date-requested').text(dif + timeframe);
    $('.tooltipped').tooltip();
    toggleViewAssessor();
    const modal = M.Modal.getInstance($('#request-modal'));
    modal.open();
  });
}

function sendResponse() {
  const form = $('#respond-form');
  const assessor = form.find('select[name="assessor"]');
  const accepted = $('#accept-check').prop('checked');
  if (accepted && assessor.val() === null) {
    flash('You must select an assessor!', true);
    return;
  }

  makeRequest('/respond_request', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
      return;
    }
    if (accepted) {
      delayToast('Request approved!<br>Student has been notified');
    } else {
      delayToast('Request rejected!<br>Student has been notified');
    }
    location.reload();
  });
}

$(function () {
  /* initialise materalize style select statements */
  $('#reject-check').change(function () {
    toggleViewAssessor();
  });
  $('#accept-check').change(function () {
    toggleViewAssessor();
  });

  /* fix the select assessor box in the modal */
  /* https://github.com/Dogfalo/materialize/issues/1385 */
  M.FormSelect.init($('#assessor-select'), {dropdownOptions: { container: document.body }});
});
