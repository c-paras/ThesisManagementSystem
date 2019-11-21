let canRequest;
let entriesPerPage;

function makeCard(id, title, description, topics, supervisor, email, preqs, visible) {
  let badge = '';
  if (!visible) {
    badge = '<span class="new badge red" data-badge-caption="">Not on offer</span>';
  }
  let topicBadges = '';
  let preqBadges = '';
  for (const topic of topics.split(',')) {
    topicBadges += `<span class="new badge badge-search" data-badge-caption="">${topic}</span>`;
  }
  for (const preq of preqs.split(',')) {
    preqBadges += `<span class="new badge badge-search" data-badge-caption="">${preq}</span>`;
  }
  const card = `<div class="row">
  <div class="col s12">
    <div class="card white-grey darken-1">
      <div class="card-content black-text">
        <span class="card-title">${title}</span>
          <p>
            <span class="left" style="padding-bottom: 5px;">
              <i class="material-icons tiny teal-text disable-icon">bookmark</i>
              <span style="padding-bottom: 20px;">Topic Area(s):</span> ${topicBadges}
            </span>
            ${badge}
          </p><br>
          <hr>
        </span>
        <p>
          <i class="material-icons tiny teal-text disable-icon">person</i>
          Supervisor: ${supervisor}
          <a href="mailto:${email}" target="_top"> (${email})</a>
        </p>
        <p id="preqs" class="left" style="padding-bottom: 20px;">
          <i class="material-icons tiny teal-text disable-icon">check_circle</i>
          Prerequisite(s): ${preqBadges}
        </p>
        <br><br>
        <p>${description}</p>
      </div>
      <div class="card-action">
        <a
          name="request-btn" class="modal-trigger"
          href="#request-modal" onclick="loadTopic(${id}, '${supervisor}')"
          visible="${visible}"
        >
          Request Topic
        </a>
      </div>
    </div>
  </div>
  </div>`;
  return card;
}

function disableTopicRequest(elem, msg) {
  elem.attr('href', '#!');
  elem.prop('onclick', null);
  elem.removeClass('modal-trigger');
  elem.click(function () {
    flash(msg, error = true);
  });
}

function updateCanRequest() {
  $('[name="request-btn"]').each(function () {
    if ($(this).attr('visible') === '0') {
      disableTopicRequest($(this), 'This topic is not available for request!');
    }
  });
  if (!canRequest) {
    $('[name="request-btn"]').each(function () {
      disableTopicRequest($(this), 'Only students enrolled in a thesis course may request a topic!');
    });
  }
}

function nextPage(requestedPage) {
  let cards = $.myTopicCards;
  $('#search-results').html(
    cards.slice(requestedPage * entriesPerPage - entriesPerPage, requestedPage * entriesPerPage)
  );
  $(window).scrollTop($('a#search-btn').offset().top);
  updateCanRequest();
}

function searchResults() {
  const form = $('#search-form');
  if (!formValid(form)) {
    return;
  }

  const data = {
    'searchTerm': $('#search-input').val(),
    'checkbox': $('#checkbox-vis').is(':checked'),
    'topicArea': M.Chips.getInstance($('#topics')).chipsData,
    'supervisor': M.Chips.getInstance($('#supervisor')).chipsData,
    'sortBy': form.find('[name=sortby]').val()
  };
  makePOSTRequest('/search', data, (res) => {
    if (res.status === 'fail') {
      flash(res.message, error = true);
    } else {
      let cards = [];
      for (const i in res.topics) {
        topic = res.topics[i];
        let preqs = 'None';
        if (topic.preqs.length !== 0) {
          const preqList = topic.preqs.map(value => value.code);
          preqs = preqList.join(', ');
        }
        cards.push(makeCard(topic.id, topic.title, topic.description,
                            topic.areas.join(', '), topic.supervisor.name,
                            topic.supervisor.email, preqs, topic.visible));
      }

      $("[id='tagsTopic']").val('');
      $("[id='tagsSupervisor']").val('');

      if (res.topics.length > 0) {
        $('#search-title').html('Search Results (found ' + res.topics.length + ' matching topics):');
      } else {
        $('#search-title').html('Your search returned no matching topics');
      }

      entriesPerPage = $('#entries').val();
      if (entriesPerPage === 'infinite') {
        entriesPerPage = cards.length;
      }
      $.myTopicCards = cards;

      $('#search-title').show();
      $('#search-results').html(cards.slice(0, entriesPerPage));
      $('#page').html('');
      if (res.topics.length > 0) {
        $('#page').materializePagination({
          align: 'center',
          lastPage: Math.ceil(cards.length / entriesPerPage),
          firstPage: 1,
          useUrlParameter: false,
          onClickCallback: function (requestedPage) {
            nextPage(requestedPage);
          }
        });
      }

      canRequest = res.canRequest;
      updateCanRequest();
    }
  });
}

function loadPage() {
  makeGETRequest('/search_chips', (res) => {

    $('#topics').chips({
      placeholder: 'Enter a Topic Area',
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

$(function () {
  loadPage();
  $('#checkbox-vis').change(searchResults);
  $('#search-form').find('select[name=sortby]').change(searchResults);
  $('#search-form').find('input[name=strict-match]').change(searchResults);
  $('#entries').change(searchResults);
});

function showAdvanced() {
  if ($('#advanced-menu').is(':visible')) {
    $(event.target).find('i').text('arrow_drop_down');
    $('#advanced-menu').hide();
  } else {
    $(event.target).find('i').text('arrow_drop_up');
    $('#advanced-menu').show();
  }
}
