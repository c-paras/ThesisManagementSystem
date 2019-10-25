function submitRequest() {
  const form = $('#request-form');
  if (!formValid(form)) {
    return;
  }
  makeRequest('/request_topic', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      flash('Request sent!', error = false);
      $('#request-modal').modal('close');
    }
  });
}

function loadTopic(topic) {
  $('#request-form').find('#topic').val(topic);
}
