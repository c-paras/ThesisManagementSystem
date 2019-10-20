console.log('Client side javascript file is loaded');


window.onload = function initChips(event) {
    $('.chips').chips();
    $('.chips-placeholder').chips({
        placeholder: 'Enter a topic',
        secondaryPlaceholder: '+Tag',
    });

    $('.chips-autocomplete').chips({
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

function searchResults() {
    const form = $('#search-form');
    if (!formValid(form)) {
        return;
    }

    makeRequest('/search', form, (res) => {
        if (res.status === 'fail') {
          flash(res.message, error = true);
        } else {
            console.log(res)
            //const results = document.querySelector("#para")
            //results.textContent = res.topics[0][0]
            var cards = ""
            console.log(res.topics)
            for (i=0; i < res.topics.length; i++) {
                console.log("yello")
                cards = cards + makeCard(res.topics[i][0], res.topics[i][2])
             }

          document.getElementById("results").innerHTML = cards
        }
    });
}

function makeCard(title, description) {
    var card = `<div class="row">\
    <div class="col s12 m6">\
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
  </div>`

  return card
}