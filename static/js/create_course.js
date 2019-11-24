function createCourse() {
  const form = $('#create-course-form');
  if(!formValid(form)) {
    return;
  }

  const selectBox = M.FormSelect.getInstance(form.find('select[name=year]')[0]);
  // Can't use getSelectedValues() due to bug https://github.com/Dogfalo/materialize/issues/6123
  if(selectBox.el.selectedIndex === 0) {
    flash('You must select a year for the course offering', true);
    return;
  }

  let checked = false;
  $('#term-offers').find('input[type=checkbox]').each(function() {
    if($(this).prop('checked') === true) {
      checked = true;
    }
  });
  if(checked === false) {
    flash('You must select at least one term offering', true);
    return;
  }
  makeRequest('/create_course', form, (res) => {
    if (res.status === 'fail') {
      flash(res.message, true);
      if (res.field) {
        markFieldValid($(`#${res.field}`), false);
      }
      return;
    }
    if(location.href.includes('manage_courses')) {
      delayToast('Course created');
      window.location.href = location.href.replace('#!', '');
    } else {
      flash('Course created');
      $('#create-course-modal').modal('close');
    }
  });
}

function openCreateCourseModal() {
  const form = $('#create-topic-form');
  // Materialize makes a select have a text area, ignore it
  form.find('input[type=text], textarea').not('[readonly]').each(function() {
    $(this).val('');
  });

  $('#create-course-modal').modal('open');
}
