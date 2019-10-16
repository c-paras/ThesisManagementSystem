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
  form.find('input').each(function () {
    if ($(this).val() === '') {
      invalid = true;
    }
  });
  return !(invalid || form.find('.invalid').length);
}

/*
 * Make an API call to the backend and call the specified
 * callback function to process the JSON response.
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
