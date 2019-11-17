function updateTopicVisibility(id) {
  const form = $('#manage-topic-form');
  if (!formValid(form)) {
    return;
  }

  const data = {};
  $('input[type="checkbox"]').each(function () {
    const status = $(this).is(':checked');
    const id = $(this).attr('id');
    data[id] = status;
  });

  makePOSTRequest('/manage_topics', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      if (id === undefined) {
        flash('All topics are now unavailable students', false);
      } else {
        if ($(`#${id}`).is(':checked')) {
          flash('Topic is now visible to students', false);
        } else {
          flash('Students can no longer view the topic', false);
        }
      }
    }
  });
}

function deleteTopic(topicId) {
  
  const data = {
    "topicId": topicId
  };

  makePOSTRequest('/delete_topic', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast(res.message);
      location.reload();
    }
  });
}
function openTopicDeleteConfirmation(topicName, topicId) {
  let text = 'Are you sure you want to delete the Material: ' + topicName;
  $('#deletion-message').text(text);
  $('#confirm-deletion').click(function callDelet() {
    deleteTopic(topicId);
  });
  $('#deleteModal').modal('open');
}

$('#checkall-btn').on('click', function () {
  $('input[type="checkbox"]').prop('checked', false);
  updateTopicVisibility();
});

$(document).ready(function(){
  $('.modal').modal();
});
