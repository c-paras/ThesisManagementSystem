function toggleSubmissionType() {
  if ($('#text-type').prop('checked') === true) {
    $('#text-entry-block').show();
    $('#file-upload-block').hide();
  } else {
    $('#text-entry-block').hide();
    $('#file-upload-block').show();
  }
}

$('[name="submission-type"]').change(function () {
  toggleSubmissionType();
});

toggleSubmissionType();

function addCriteria() {
  const lastCriteria = $('#criteria-table').find('[name^="marking-criteria-"]:last');
  const newCriteria = lastCriteria.clone();
  newCriteria.find('input').each(function () {
    $(this).val('');
    markFieldValid($(this));
  });
  newCriteria.insertAfter(lastCriteria);
}

function removeCriteria(criteria) {
  const table = $('#criteria-table');
  if (table.find('tbody').find('tr').length > 2) {
    const toRemove = table.find(`#marking-criteria-${criteria}`);
    toRemove.remove();
  }
}
