function toggleSubmissionType() {
  if ($('#text-type').prop('checked') === true) {
    $('#text-entry-block').show();
    $('#file-size-block').hide();
    $('#file-type-block').hide();
  } else {
    $('#text-entry-block').hide();
    $('#file-size-block').show();
    $('#file-type-block').show();
  }
}

function toggleMarkingMethod() {
  if ($('#accept-method').prop('checked') === true) {
    $('#marking-criteria-block').hide();
  } else {
    $('#marking-criteria-block').show();
  }
}

$('[name="submission-type"]').change(function () {
  toggleSubmissionType();
});

$('[name="marking-method"]').change(function () {
  toggleMarkingMethod();
});

toggleSubmissionType();
toggleMarkingMethod();

function relabel(elem, attrs) {
  let id = 0;
  for (const attr of attrs) {
    val = elem.attr(attr);
    id = parseInt(val.match(/\d+$/)[0]);
    elem.attr(
      attr, val.replace(/(\d+)$/, function (all, n) {
        return parseInt(n) + 1;
      })
    );
  }
  return id + 1;
}

function addCriteria() {
  const lastCriteria = $('#criteria-table').find('[name^="marking-criteria-"]:last');
  const newCriteria = lastCriteria.clone();
  const id = relabel(newCriteria, ['id', 'name']);
  newCriteria.find('input').each(function () {
    relabel($(this), ['id', 'name']);
    $(this).val('');
    markFieldValid($(this));
  });
  newCriteria.find('[name="remove-criteria"]').attr('onclick', `removeCriteria(${id})`);
  newCriteria.insertAfter(lastCriteria);
}

function removeCriteria(criteria) {
  const table = $('#criteria-table');
  if (table.find('tbody').find('tr').length > 2) {
    const toRemove = table.find(`#marking-criteria-${criteria}`);
    toRemove.remove();
  }
}

$('#word-limit').on('input, change, keydown', function () {
  const val = $(this).val();
  if ($(this).hasClass('invalid')) {
    const max = parseInt($(this).attr('max'));
    if (val.match(/^\d+$/) && parseInt(val) > max) {
      $('#word-limit-error').attr('data-error', `Maximum word limit is ${max}`);
    } else if (!val.match(/^\d+$/)) {
      $('#word-limit-error').attr('data-error', 'Word limit is required');
    }
  }
});
