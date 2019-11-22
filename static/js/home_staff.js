let interval;

function requestTimestamp(reqDate) {
  const d = new Date(reqDate);
  let dif = new Date(new Date() - d) / 1000;
  let plural = (Math.floor(dif) === 1) ? '' : 's';
  let timeframe = `second${plural} ago`;
  let seconds = true;

  if (dif > 60) {
    dif /= 60;
    plural = (Math.floor(dif) === 1) ? '' : 's';
    timeframe = `minute${plural} ago`;
    seconds = false;
  }

  if (dif > 60) {
    dif /= 60;
    plural = (Math.floor(dif) === 1) ? '' : 's';
    timeframe = `hour${plural} ago`;
  }

  if (dif > 24 && timeframe === `hour${plural} ago`) {
    dif /= 24;
    plural = (Math.floor(dif) === 1) ? '' : 's';
    timeframe = `day${plural} ago`;
  }

  dif = Math.floor(dif);
  const date = d.getDate();
  const year = d.getFullYear();
  let hour = d.getHours();
  hour = (hour < 10) ? `0${hour}` : hour;
  let minutes = d.getMinutes();
  minutes = (minutes < 10) ? `0${minutes}` : minutes;
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const monthCode = months[d.getMonth()];
  const dateString = (date + ' ' + monthCode + ' ' +
    year + ' ' + hour + ':' + minutes);

  if (seconds) {
    $('#date-requested').text(`about ${dif} ${timeframe}`);
  } else {
    $('#date-requested').text(`${dif} ${timeframe}`);
  }

  return dateString;
}

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

    clearInterval(interval);
    const dateString = requestTimestamp(res.reqDate);
    $('#date-requested').attr('data-tooltip', dateString);
    $('.tooltipped').tooltip();
    interval = setInterval(function () {
      requestTimestamp(res.reqDate);
    }, Math.random() * (12000 - 4000) + 4000);

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
