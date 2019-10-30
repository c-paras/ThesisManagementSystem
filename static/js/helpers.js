/*
 * Invoke a Materialize "toast" message, clearing
 * any previous toasts to prevent clutter.
 */
function flash(msg, error = false) {
  M.Toast.dismissAll();
  const color = (error) ? 'red' : 'blue';
  M.toast({html: msg, classes: `${color} darken-1 rounded`});
}

/*
 * Mark a field as valid or invalid, by setting the
 * appropriate Materialize class.
 */
function markFieldValid(field, valid) {
  if (valid) {
    field.removeClass('invalid');
    field.addClass('valid');
  } else {
    field.removeClass('valid');
    field.addClass('invalid');
  }
}

/*
 * Check whether a form is valid by ensuring all its
 * fields have data and are not marked as invalid by Materialize.
 */
function formValid(form) {
  let invalid = false;
  form.find('input,textarea').each(function () {
    if ($(this).val() === '' && $(this).attr('required')) {
      invalid = true;
    }
  });
  return !(invalid || form.find('.invalid').length);
}

/*
 * Make a POST request to the backend with a serialized form.
 * Call the specified callback function to process the JSON response.
 */
function makeRequest(endpoint, form, callback) {
  fetch(endpoint, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    },
    method: 'POST',
    body: form.serialize()
  })
  .then(res => res.json())
  .then(callback);
}

/*
 * Make a GET request to the backend and call the specified callback
 * function to process the JSON response. Use this function for data
 * retrieval from the backend.
 */
function makeGETRequest(endpoint, callback) {
  fetch(endpoint, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    },
    method: 'GET'
  })
  .then(res => res.json())
  .then(callback);
}

function searchResultsNavBar() {
  const searchTerms = $("#search-bar").val();
  console.log("hello");
  window.location.href = '/search?terms=' + searchTerms;
  
}

/*
 * Make a POST request to the backend and call the specified callback
 * function to process the JSON response. Use this function for posting
 * data to the backend that is not inside a form.
 */
function makePOSTRequest(endpoint, data, callback) {
  fetch(endpoint, {
    headers: {
      'Content-Type': 'Content-Type: multipart/form-data',
      'Accept': 'application/json'
    },
    method: 'POST',
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(callback);
}

/*
 * Load toast message into localStorage for display on subsequent page load.
 */
function delayToast(msg, err) {
  localStorage.setItem('msg', msg);
  localStorage.setItem('error', err);
}

/*
 * Show lingering "toast" message upon page reload.
 */
$(function () {
  const msg = localStorage.getItem('msg');
  const err = localStorage.getItem('error');
  if (msg !== null && err !== null) {
    flash(msg, eval(err)); /* jshint ignore:line */
  }
  localStorage.removeItem('msg');
  localStorage.removeItem('error');
});

/*
 * Enable forms on page to be submitted by pressing the enter/return key.
 */
$(function () {
  $('form').not('.modal-form').each(function () {
    const form = $(this);
    const submit = form.find('a:last');

    /* to prevent form submission in textaea fields */
    form.find('input').each(function () {
      /* to prevent form submission in chips fields */
      if (!$(this).parent().hasClass('enter-no-submit')) {
        $(this).keydown(function (event) {
          if (event.keyCode === 13) {
            submit.click();
            return false;
          }
        });
      }
    });

  });
});

/*
 * Manually add and remove active class from chips fields.
 * This makes chips fields consistent with normal input fields.
 */
$(function () {
  $('.chips input').on('focus', function () {
    $(this).parent().siblings('.prefix').addClass('active');
  });

  $('.chips input').on('blur', function () {
    $(this).parent().siblings('.prefix').removeClass('active');
  });
});

$('#search-bar').keydown(function(e){
  if (e.keyCode === 13) { // If Enter key pressed
      $(this).trigger('submit');
  }
});
