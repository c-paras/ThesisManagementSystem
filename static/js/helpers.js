/*
 * Invoke a Materialize "toast" message, clearing
 * any previous toasts to prevent clutter.
 */
function flash(msg, error = false) {
  M.Toast.dismissAll();
  const color = (error) ? 'red' : 'blue';
  if (!msg) {
    msg = 'Undefined message.';
  }
  if (msg && !(msg.endsWith('.') || msg.endsWith('!'))) {
    if (msg.includes('!')) {
      msg += '.';
    } else {
      msg += '!';
    }
  }
  M.toast({html: msg, classes: `${color} darken-1 rounded`});
}

/*
 * Mark a field as valid or invalid, by setting the
 * appropriate Materialize class. If the valid state is not
 * specified, both validation classes are removed.
 */
function markFieldValid(field, valid) {
  if (valid === undefined) {
    field.removeClass('invalid');
    field.removeClass('valid');
  } else if (valid) {
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
  form.find('input, textarea').each(function () {
    if ($(this).val().match(/^\s*$/) && $(this).attr('required')) {
      const requiredIf = $(this).attr('requiredif');
      let notRequired = false;
      if (requiredIf) {
        /* handle fields that are optionally required */
        const req = requiredIf.split('=');
        if ($(`[name='${req[0]}']:checked`).val() !== req[1]) {
          notRequired = true;
        }
      }
      if (!notRequired) {
        invalid = true;
      }
      markFieldValid($(this), notRequired);
    }
    if (!invalid && !$(this).attr('pattern') && $(this).attr('required')) {
      markFieldValid($(this), true);
    }
  });
  return !invalid;
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
 * Make a POST request to the backend with a multipart form, only
 * supports a single file. Call the specified callback function to
 * process the JSON response.
 */
function makeMultiPartRequest(endpoint, form, callback) {
  const data = new FormData();
  data.append('file', form.find('input[type="file"]')[0].files[0]);
  form.find('input[type!="file"], textarea, select').each(function (index, value) {
    if ($(value).attr('name')) {
      if ($(value).attr('type') && $(value).attr('type') === 'radio') {
        if ($(value).is(':checked')) {
          data.append($(value).attr('name'), $(value).val());
        }
      } else {
        data.append($(value).attr('name'), $(value).val());
      }
    }
  });
  fetch(endpoint, {
    headers: {
      'Accept': 'application/json'
    },
    method: 'POST',
    body: data
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

    /* prevent form submission in textarea fields */
    form.find('input').each(function () {
      /* prevent form submission in chips fields */
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
 * Prevent fields containing only spaces from being treated as valid.
 * The `pattern' attribute is not supported for textareas yet.
 */
$(function () {
  $('body').find('input, textarea').each(function () {
    $(this).on('input', function () {
      const val = $(this).val();
      if (val.match(/^\s+$/)) {
        $(this).val(val.trim());
      }
    });
  });
});

/*
 * Manually add and remove active class from chips fields.
 * This makes chips fields consistent with normal input fields.
 */
$(function () {
  const observer = new MutationObserver(function (mutations) {
    for (const elem of mutations) {
      const elemId = elem.target.getAttribute('id');
      if (elem.target.getAttribute('class').includes('focus')) {
        $(`#${elemId}`).parent().find('.prefix').addClass('active');
      } else {
        $(`#${elemId}`).parent().find('.prefix').removeClass('active');
      }
    }
  });
  for (const elem of document.getElementsByClassName('chips')) {
    observer.observe(elem, {
      attributes: true,
      attributeFilter: ['class'],
      childList: false,
      characterData: false
    });
  }
});

/*
 * Automatically convert text in a chips field into a chip
 * when the user leaves the field. The time delays ensure
 * the adding of a chip is synchronized better with respect
 * to Materialize's own chip-adding functionality. It prevents
 * a chip being added inadvertently if Materialize is also adding
 * the chip at the same time, e.g. via the autocomplete field.
 */
$(function () {
  setTimeout(function () {
    $('body').find('.chips').each(function () {
      const elem = $(this);
      M.Chips.getInstance(elem).$input.on('blur', function () {
        const chipsInputField = M.Chips.getInstance(elem).$input;
        setTimeout(function () {
          const stringNotInChip = chipsInputField.val();
          if (stringNotInChip) {
            M.Chips.getInstance(elem).addChip({
              tag: stringNotInChip
            });
            chipsInputField.val('');
          }
        }, 200);
      });
    });
  }, 1000);
});
