function submitRequest() {
  const form = $('#request-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/request_topic', form, (res) => {
    $('#request-modal').modal('close');
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      flash('Request sent!', error = false);
    }
  });
}

function loadTopic(topic) {
  $('#request-form').find('#topic').val(topic);
}
