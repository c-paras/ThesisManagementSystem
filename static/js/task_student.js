function updateAllOwnWork() {
    if($('#all-own-work').prop('checked')) {
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
    delayToast("Success");
    location.reload();
  });
}

function countWords(str) {
    if(str.trim() === ""){
        return 0;
    }
    return str.trim().concat(' ').split(/\s+/).length-1;
}

function updateWordCount(textarea){
    $('#word-counter').html(countWords($(textarea).val()));
}

function uploadText(btn) {
  if($('#textarea1').val().trim().length === 0) {
    flash('Your must enter some text to submit', true);
    return;
  }

  if(countWords($('#textarea1').val()) > parseInt($('#word_limit').val())) {
    flash('Your submission is above the word limit', true);
    return;
  }

  updateAllOwnWork();
  if ($('#all-own-work').prop('checked') !== true) {
    flash('You must certify this is all your own work', true);
    return;
  }

  const form = $('#text-upload-form');

  makeRequest('/submit_text_task', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, true);
      return;
    }
    delayToast("Submission accepted!", false);
    location.reload();
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

function openTextEditor(){
  updateWordCount($('#textarea1'));
  $('#all-own-work').prop('checked', false);
  $("#view_text_section").hide();
  $("#edit_text_section").show();
}

function closeTextEditor(){
  $('#textarea1').val("");
  $('#all-own-work').prop('checked', false);
  $("#view_text_section").show();
  $("#edit_text_section").hide();
}
