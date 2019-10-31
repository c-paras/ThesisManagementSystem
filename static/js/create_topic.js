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

  makePOSTRequest('/create_topic', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Topic created', false);
      window.location.href = '/home';
    }
  });
}

function loadTopicPrereq() {
  makeGETRequest('/load_topic_prereqs', (res) => {
    $('#prereqs').chips({
      placeholder: 'Add Prerequisite',
      autocompleteOptions: {
        data: res.chipsPrereqs,
        limit: 10,
        minLength: 1
      }
    });
    $('#areas').chips({
      placeholder: 'Add Topic Area',
      autocompleteOptions: {
        data: res.chipsTopic,
        limit: 10,
        minLength: 1
      }
    });
    submitCreate();
  });

}

loadTopicPrereq();