function uploadText(btn) {
    const form = $('#text-upload-form');
    if($('#all-own-work').prop('checked') !== true) {
        flash('You must certify it is all your own work', true);
        return;
    }

    if(countWords($('#textarea1').val()) > parseInt($('#word_limit').val())) {
        flash('Your submission is above the word limit', true);
        return;
    }

    $(btn).parent().children().each(function(index, value) {
        $(value).toggle();
    });
    makeRequest('/submit_text_task', form, (res) => {
        $(btn).parent().children().each(function(index, value) {
            $(value).toggle();
        });
        if (res.status === 'fail') {
            flash(res.message, true);
            return;
        }
        flash("Success");
    });
}

function countWords(str) {
  return str.trim().split(/\s+/).length;
}