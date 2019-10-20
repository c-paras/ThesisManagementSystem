console.log('Client side javascript file is loaded');


window.onload = function initChips(event) {
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
}

function searchResults() {
    const form = $('#search-form');
    if (!formValid(form)) {
        return;
    }

    makeRequest('/search', form, (res) => {
        if (res.status === 'fail') {
          flash(res.message, error = true);
        } else {
          
        }
    });
}