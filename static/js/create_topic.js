function submitCreate() {
  const form = $('#create-topic-form');
  if (!formValid(form)) {
    return;
  }
  const data = {
    'topic': $('#topic').val(),
    'topic_area': M.Chips.getInstance($('#areas')).chipsData,
    'prereqs': M.Chips.getInstance($('#prereqs')).chipsData,
    'details': $('#details').val()
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

function submitEditTopic() {
  const form = $('#create-topic-form');
  if (!formValid(form)) {
    return;
  }
  const data = {
    'topic': $('#topic').val(),
    'topic_area': M.Chips.getInstance($("div[id*='areas']")).chipsData,
    'prereqs': M.Chips.getInstance($("div[id*='prereqs']")).chipsData,
    'details': $('#details').val()
  };

  const topic_id = $("div[id*='prereqs-edit']").attr('id');
  makePOSTRequest('/create_topic?update=' + topic_id, data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      delayToast('Topic edited!', false);
      window.location.href = '/home';
    }
  });
}

function loadChips() {
  if ($("div[id*='prereqs-edit']").length) {
    const topic_id = $("div[id*='prereqs-edit']").attr('id');
    makeGETRequest('/get_topic_prereqs?update=' + topic_id, (res) => {

      $("div[id*='prereqs-edit']").chips({
        placeholder: 'Add Prerequisite',
        data: res.old_prereqs,
        autocompleteOptions: {
          data: res.chips_prereqs,
          limit: 10,
          minLength: 1
        }
      });

      $("div[id*='areas-edit']").chips({
        placeholder: 'Add Topic Area',
        data: res.old_areas,
        autocompleteOptions: {
          data: res.chips_topic,
          limit: 10,
          minLength: 1
        }
      });

    });
  } else {
    makeGETRequest('/get_topic_prereqs', (res) => {

      $('#prereqs').chips({
        placeholder: 'Add Prerequisite',
        autocompleteOptions: {
          data: res.chips_prereqs,
          limit: 10,
          minLength: 1
        }
      });

      $('#areas').chips({
        placeholder: 'Add Topic Area',
        autocompleteOptions: {
          data: res.chips_topic,
          limit: 10,
          minLength: 1
        }
      });

    });
  }

}

loadChips();
