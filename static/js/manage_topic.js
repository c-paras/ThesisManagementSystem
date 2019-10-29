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
  console.log(data);

  makeRequestCustomData('/manage_topic', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Topic created!', false);
    }
  });
}