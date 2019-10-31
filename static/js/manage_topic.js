function submitManage() {
  const form = $('#manage-topic-form');
  if (!formValid(form)) {
    return;
  }
  const data = {};
  $('input[type=checkbox]').each(function () {

    const status = $(this).is(':checked');
    const id = $(this).attr("id");
    data[id] = status;
  });

  makeRequestCustomData('/manage_topic', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Changes Saved!', false);
      window.location.href = '/home';
    }
  });
}


function submitManage() {
  const form = $('#manage-topic-form');
  if (!formValid(form)) {
    return;
  }
  const data = {};
  $('input[type=checkbox]').each(function () {

    const status = $(this).is(':checked');
    const id = $(this).attr("id");
    data[id] = status;
  });

  makeRequestCustomData('/manage_topic', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Changes Saved!', false);
      window.location.href = '/home';
    }
  });
}

$('#checkall-btn').on('click', function () {
  const flag = false;

  $('input[type=checkbox]').prop('checked', flag);
  submitManage();
});