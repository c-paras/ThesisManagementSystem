let canRequest;

function makeCard(id, title, description, topics, supervisor, email) {
  const card = `<div class="row">\
  <div class="col s10 offset-m1">\
    <div class="card white-grey darken-1">
      <div class="card-content black-text">
        <span class="card-title">${title}</span>
          <p>Topic Area: ${topics}</p>
          <hr>
        </span>
        <p>Supervisor: ${supervisor}
        <a href="mailto:${email}" target="_top"> (${email})</a>
        </p>
        <p>Prerequisites: Not implemented yet waiting for db</p>
        <br>
        <p>${description}</p>
      </div>
      <div class="card-action">
        <a
          name="request-btn" class="modal-trigger"
          href="#request-modal" onclick="loadTopic(${id}, '${supervisor}')"
        >
          Request Topic
        </a>
      </div>
    </div>
  </div>
  </div>`;
  return card;
}

function updateCanRequest() {
  if (!canRequest) {
    $('[name="request-btn"]').each(function () {
      $(this).attr('href', '#!');
      $(this).prop('onclick', null);
      $(this).click(function () {
        flash('Only students enrolled in a thesis course may request a topic!', error = true);
      });
    });
  }
}

function nextPage(requestedPage) {
  let cards = $.myTopicCards;
  $('#search-results').html(cards.slice(requestedPage*10 - 10, requestedPage*10));
  $(window).scrollTop($('a#search-btn').offset().top);
  updateCanRequest();
}

function searchResults() {
  const form = $('#search-form');
  if (!formValid(form)) {
    return;
  }

  const data = {
    "searchTerm": $("[id='search-input']").val(),
    "checkbox": $("[id='checkbox-vis']").is(':checked'),
    "topicArea": M.Chips.getInstance($('#topics')).chipsData,
    "supervisor": M.Chips.getInstance($('#supervisor')).chipsData
  };

  makePOSTRequest('/search', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      let cards = [];
      for (let i = 0; i < res.topics.length; i++) {
        cards.push(makeCard(res.topics[i][0], res.topics[i][1],
          res.topics[i][3], res.topicsArea[i].join(', '),
          res.topicSupervisor[i][0][0], res.topicSupervisor[i][0][1])
        );
      }

      $("[id='tagsTopic']").each((function () {
        $(this).val('');
      }));

      $("[id='tagsSupervisor']").each((function () {
        $(this).val('');
      }));

      if (res.topics.length > 0) {
        $('#search-title').html('Search Results (found ' + res.topics.length + ' matching topics)');
      } else {
        $('#search-title').html('Your search returned no matching topics');
      }

      $.myTopicCards = cards;

      $('#search-title').show();
      $('#search-results').html(cards.slice(0, 10));
      $('#page').html('');
      $('#page').materializePagination({
        align: 'center',
        lastPage: Math.ceil(cards.length/10),
        firstPage: 1,
        useUrlParameter: false,
        onClickCallback: function(requestedPage) {
          nextPage(requestedPage);
        }
      });

      canRequest = res.canRequest;
      updateCanRequest();
    }
  });
}

function loadPage() {
  makeGETRequest('/search_chips', (res) => {

    $('#topics').chips({
      placeholder: 'Enter a topic',
      autocompleteOptions: {
        data: res.chipsTopic,
        limit: 20,
        minLength: 1
      }
    });

    $('#supervisor').chips({
      placeholder: 'Enter a supervisor',
      autocompleteOptions: {
        data: res.chipsSuper,
        limit: 20,
        minLength: 1
      }
    });

    searchResults();
  });

  return;
}

loadPage();
