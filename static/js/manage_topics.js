function updateTopicVisibility() {
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
      flash('Visibility updated', false);
    }
  });
}

$('#checkall-btn').on('click', function () {
  $('input[type="checkbox"]').prop('checked', false);
  updateTopicVisibility();
});
