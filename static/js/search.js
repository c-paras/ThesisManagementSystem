let canRequest;

function makeCard(id, title, description, topics, supervisor, email, preqs) {
  const card = `<div class="row">
  <div class="col s12">
    <div class="card white-grey darken-1">
      <div class="card-content black-text">
        <span class="card-title">${title}</span>
          <p>Topic Area: ${topics}</p>
          <hr>
        </span>
        <p>Supervisor: ${supervisor}
        <a href="mailto:${email}" target="_top"> (${email})</a>
        </p>
        <p id="preqs">Prerequisites: ${preqs}</p>
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
  $('#search-results').html(cards.slice(requestedPage * 10 - 10, requestedPage * 10));
  $(window).scrollTop($('a#search-btn').offset().top);
  updateCanRequest();
}

function searchResults() {
  const form = $('#search-form');
  if (!formValid(form)) {
    return;
  }

  let data = {
    'searchTerm': $('#search-input').val(),
    'checkbox': $('#checkbox-vis').is(':checked'),
    'topicArea': M.Chips.getInstance($('#topics')).chipsData,
    'supervisor': M.Chips.getInstance($('#supervisor')).chipsData
  };

  makePOSTRequest('/search', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      let cards = [];
      for (const i in res.topics) {
        topic = res.topics[i];
        let preqs = 'None';
        if(topic.preqs.length !== 0) {
          const preqList = topic.preqs.map(value => value.code);
          preqs = preqList.join(', ');
        }
        cards.push(makeCard(topic.id, topic.title, topic.description,
                            topic.areas.join(', '), topic.supervisor.name,
                            topic.supervisor.email, preqs));
      }

      $("[id='tagsTopic']").each((function () {
        $(this).val('');
      }));

      $("[id='tagsSupervisor']").each((function () {
        $(this).val('');
      }));

      if (res.topics.length > 0) {
        $('#search-title').html('Search Results (found ' + res.topics.length + ' matching topics):');
      } else {
        $('#search-title').html('Your search returned no matching topics');
      }

      const entriesPerPage = $('#entries').val();
      $.myTopicCards = cards;

      $('#search-title').show();
      $('#search-results').html(cards.slice(0, entriesPerPage));
      $('#page').html('');
      $('#page').materializePagination({
        align: 'center',
        lastPage: Math.ceil(cards.length / entriesPerPage),
        firstPage: 1,
        useUrlParameter: false,
        onClickCallback: function (requestedPage) {
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
      placeholder: 'Enter a Topic',
      autocompleteOptions: {
        data: res.chipsTopic,
        limit: 20,
        minLength: 1
      }
    });

    $('#supervisor').chips({
      placeholder: 'Enter a Supervisor',
      autocompleteOptions: {
        data: res.chipsSuper,
        limit: 20,
        minLength: 1
      }
    });

    searchResults();
  });
}

$(function() {
  loadPage();
});


function showAdvanced() {
  $(event.target).toggle();
  $('#advanced-menu').toggle();
}
