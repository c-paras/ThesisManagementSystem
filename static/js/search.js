$('#topics').chips();
$('#topics').chips({
    placeholder: 'Enter a topic',
    secondaryPlaceholder: '+Tag',
});

$('#topics').chips({
    autocompleteOptions: {
      data: {
        'Robotics': null,
        'Graphics': null,
        'User Interfaces': null,
        'Formal Methods': null,
      },
      limit: Infinity,
      minLength: 1
    }
  });

$('#supervisor').chips();
$('#supervisor').chips({
    placeholder: 'Enter Supervisor',
    secondaryPlaceholder: '+Tag',
});

$('#supervisor').chips({
    autocompleteOptions: {
      data: {
        'z7654321': null,
        'z0001112': null,
        'z8000003': null,
        'z8000001': null,
      },
      limit: Infinity,
      minLength: 1
    }
  });



function makeCard(title, description, topics, supervisor) {
    var card = `<div class="row">\
    <div class="col s10 offset-m1">\
      <div class="card white-grey darken-1">\
        <div class="card-content black-text">\
          <span class="card-title">${title}</span>
            <p>Topic Area: ${topics}</p>
            <hr>
          </span>\
          <p>Supervisor: ${supervisor}</p>
          <p>${description}</p>\
        </div>\
        <div class="card-action">\
          <a href="#">Request Topic</a>\
        </div>\
      </div>\
    </div>\
  </div>`;

  return card;
}

function searchResults() {
    const form = $('#search-form');
    if (!formValid(form)) {
        return;
    }

    var tagData = M.Chips.getInstance($('#supervisor')).chipsData;
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
            console.log(res);
            //const results = document.querySelector("#para")
            //results.textContent = res.topics[0][0]
            var cards = "";
            console.log(res.topics);
            for (i=0; i < res.topics.length; i++) {
                cards = cards + makeCard(res.topics[i][1], res.topics[i][3], res.topicsArea[i], res.topicSupervisor[i]);
             }
            
            // for (let i = 0; i < $('form').length; i++) {
            //     console.log(i)
            //     $('form')[i].reset()
            // }
            $("[id='tagsTopic']").each((function() {
              $(this).val('');
            }));

            $("[id='tagsSupervisor']").each((function() {
              $(this).val('');
            }));
            
            document.getElementById("results").innerHTML = cards;
        }
    });
}

