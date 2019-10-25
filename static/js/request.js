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

function loadTopic(topic, supervisor) {
  const msg = $('#request-form').find('#message');

  /* Load supervisor of selected topic into header */
  if (msg.val().match(/^\s*Dear[^\n]*\n/)) {
    msg.val(msg.val().replace(/^\s*Dear[^\n]*\n/, `Dear ${supervisor}\n`));
  } else {
    const newMsg = msg.val().replace(/^\n*/, '\n');
    msg.val(`Dear ${supervisor}\n${newMsg}`);
  }

  /* Load selected topic id into hidden field */
  $('#request-form').find('#topic').val(topic);
}
