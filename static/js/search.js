console.log('Client side javascript file is loaded');


window.onload = function initChips(event) {
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
            'User Interface': null
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
            'Robotics': null,
            'Graphics': null,
            'User Interface': null
          },
          limit: Infinity,
          minLength: 1
        }
      });

};

function makeCard(title, description) {
    var card = `<div class="row">\
    <div class="col s8 offset-m2">\
      <div class="card white-grey darken-1">\
        <div class="card-content black-text">\
          <span class="card-title">${title}</span>\
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
    console.log(JSON.stringify(M.Chips.getInstance($('.chips')).chipsData))
    console.log(form)
    if (!formValid(form)) {
        return;
    }

    var tagData = M.Chips.getInstance($('#supervisor')).chipsData
    if (tagData.length > 0) {
        for (var i = 0; i < tagData.length; i++) {
            console.log("cool")
            $('form').append('<input type="hidden" name="tags" value="' + tagData[i].tag + '" />');
        }
    }

    var tagData = M.Chips.getInstance($('#topics')).chipsData
    if (tagData.length > 0) {
        for (var i = 0; i < tagData.length; i++) {
            console.log("cool")
            $('form').append('<input type="hidden" name="tags" value="' + tagData[i].tag + '" />');
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
                console.log("yello");
                cards = cards + makeCard(res.topics[i][0], res.topics[i][2]);
             }

          document.getElementById("results").innerHTML = cards;
        }
    });
}

