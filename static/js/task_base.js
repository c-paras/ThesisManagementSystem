function updateAllOwnWork() {
  if ($('#all-own-work').prop('checked')) {
    $('#all-own-work').val('true');
  } else {
    $('#all-own-work').val('true');
  }
}

function uploadFile() {
  const form = $('#file-upload-form');
  if ($('#file-name').val() === '') {
    flash('Please specify a file', true);
    return;
  }
  updateAllOwnWork();
  if ($('#all-own-work').prop('checked') !== true) {
    flash('You must certify this is all your own work', true);
    return;
  }
  $('#upload-spinner').toggle();
  $('#submit-btn').toggle();
  $('#cancel-btn').toggle();
  makeMultiPartRequest('/submit_file_task', form, (res) => {
    if (res.status === 'fail') {
      $('#upload-spinner').toggle();
      $('#submit-btn').toggle();
      $('#cancel-btn').toggle();
      flash(res.message, true);
      return;
    }
    delayToast("Submission accepted", false);
    window.location.href = location.href;
  });
}

function countWords(str) {
  if (str.trim() === "") {
    return 0;
  }
  return str.trim().concat(' ').split(/\s+/).length - 1;
}

function updateWordCount(textarea) {
  $('#word-counter').html(countWords($(textarea).val()));
}

function uploadText(btn) {
  const form = $('#text-upload-form');
  formValid(form); /* auto-validate, but proceed to show errors below */

  if ($('#textarea1').val().trim().length === 0) {
    flash('Your must enter some text to submit', true);
    return;
  }

  if (countWords($('#textarea1').val()) > parseInt($('#word_limit').val())) {
    flash('Your submission exceeds the word limit', true);
    return;
  }

  updateAllOwnWork();
  if ($('#all-own-work').prop('checked') !== true) {
    flash('You must certify this is all your own work', true);
    return;
  }

  makeRequest('/submit_text_task', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, true);
      return;
    }
    delayToast("Submission accepted!", false);
    window.location.href = location.href;
  });
}

function editFileSubmission() {
  $('#file-upload-form').show();
  $('#view-file-section').hide();
}

function cancelFileSubmission() {
  $('#file-upload-form').hide();
  $('#view-file-section').show();
}

function openTextEditor() {
  updateWordCount($('#textarea1'));
  $('#all-own-work').prop('checked', false);
  $("#view_text_section").hide();
  $("#edit_text_section").show();
}

function closeTextEditor() {
  $('#textarea1').val("");
  $('#all-own-work').prop('checked', false);
  $("#view_text_section").show();
  $("#edit_text_section").hide();
}

function updateMarks(taskId, studentid, taskCriteriaId, taskMax) {
  const form = $('#mark-form');
  if (!formValid(form)) {
    return;
  }

  let marks = [];

  $("[id^='enteredMark']").each((function() {
    marks.push($(this).val());
  }));

  let feedback = [];
  $("[id^='enteredFeedback']").each((function() {
    feedback.push($(this).val());
  }));

  const data = {
    'marks': marks,
    'feedback': feedback,
    'taskId': taskId,
    "studentId": studentid,
    "taskCriteria": taskCriteriaId,
    "taskMax": taskMax
  };

  if ($("#approveCheck").val() !== undefined) {
    data.approveCheck = $("#approveCheck").is(':checked');
  }

  makePOSTRequest('/mark_task', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast("Marks successfully saved", false);
      window.location.href = location.href;
    }
  });
}
