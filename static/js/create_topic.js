$('#prereqs').chips({
  placeholder: 'Add Prerequisite',
  limit: 10
});

$('#areas').chips({
  placeholder: 'Add Topic Area',
  limit: 10
});

function submitCreate() {
  const form = $('#create-topic-form');
  if (!formValid(form)) {
    return;
  }
  const data = {
    "topic": $("[id='topic']").val(),
    "topic_area": M.Chips.getInstance($('#areas')).chipsData,
    "prereqs": M.Chips.getInstance($('#prereqs')).chipsData,
    "details": $("[id='details']").val()
  };

  makeRequestCustomData('/create_topic', data, (res) =>{
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Topic created', false);
      window.location.href = '/home';
    }
  });
}
