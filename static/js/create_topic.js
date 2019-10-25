$('#prereqs').chips({
  placeholder: 'Add Prerequisite',
  limit: 20
});

function submitCreate() {
  const form = $('#create-topic-form');
  if (!formValid(form)) {
    return;
  }
  const prereqs = M.Chips.getInstance($('#prereqs')).chipsData;
  if (prereqs.length > 0) {
    for (let i = 0; i < prereqs.length; i++) {
      $('form').append('<input type="hidden" name="prerequisites" id="prerequisites" value="' + prereqs[i].tag + '" />');
    }
  }
  makeRequest('/create_topic', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Topic created!', false);
      window.location.href = '/home';
    }
  });
}
