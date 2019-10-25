$('#topics').chips({
  placeholder: 'Enter a topic',
  autocompleteOptions: {
    data: {
      'Robotics': null,
      'Graphics': null,
      'User Interfaces': null,
      'Formal Methods': null
    },
    limit: 20,
    minLength: 1
  }
});

$('#supervisor').chips({
  placeholder: 'Enter supervisor',
  autocompleteOptions: {
    data: {
      'z7654321': null,
      'z0001112': null,
      'z8000003': null,
      'z8000001': null
    },
    limit: 20,
    minLength: 1
  }
});

function makeCard(id, title, description, topics, supervisor) {
  const card = `<div class="row">\
  <div class="col s10 offset-m1">\
    <div class="card white-grey darken-1">
      <div class="card-content black-text">
        <span class="card-title">${title}</span>
          <p>Topic Area: ${topics}</p>
          <hr>
        </span>
        <p>Supervisor: ${supervisor}</p>
        <p>Prerequisites: Not implemented yet waiting for db</p>
        <br>
        <p>${description}</p>
      </div>
      <div class="card-action">
        <a
          name="request-btn" class="modal-trigger"
          href="#request-modal" onclick="loadTopic(${id})"
        >
          Request Topic
        </a>
      </div>
    </div>
  </div>
  </div>`;
  return card;
}

function searchResults() {
  const form = $('#search-form');
  if (!formValid(form)) {
    return;
  }

  let tagData = M.Chips.getInstance($('#supervisor')).chipsData;
  if (tagData.length > 0) {
    for (let i = 0; i < tagData.length; i++) {
      $('form').append('<input type="hidden" name="tagsSupervisor" id="tagsSupervisor" value="' + tagData[i].tag + '" />');
    }
  }

  tagData = M.Chips.getInstance($('#topics')).chipsData;
  if (tagData.length > 0) {
    for (let i = 0; i < tagData.length; i++) {
      $('form').append('<input type="hidden" name="tagsTopic" id="tagsTopic" value="' + tagData[i].tag + '" />');
    }
  }

  makeRequest('/search', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      let cards = '';
      for (let i = 0; i < res.topics.length; i++) {
        cards += makeCard(res.topics[i][0], res.topics[i][1],
          res.topics[i][3], res.topicsArea[i].join(', '), res.topicSupervisor[i]);
      }

      $("[id='tagsTopic']").each((function () {
        $(this).val('');
      }));

      $("[id='tagsSupervisor']").each((function () {
        $(this).val('');
      }));

      $('#search-title').html(`Search Results (found ${res.topics.length} matching topics)`);
      $('#search-title').show();
      $('#search-results').html(cards);

      if (!res.canRequest) {
        $('[name="request-btn"]').each(function () {
          $(this).attr('href', '#!');
          $(this).click(function () {
            flash('Only students enrolled in a thesis course may request a topic!', error = true);
          });
        });
      }
    }
  });
}
