

function openModal(){
    const modal = M.Modal.init($('#text_modal'), {
                                dismissible: false
                               });
    modal[0].open();
}

function closeModal(){
    const modal = M.Modal.getInstance($('#text_modal'));
    modal.close();
}

function countWords(str) {
  return str.trim().split(/\s+/).length;
}

function uploadText(btn) {
    if($('#textarea1').val().trim().length === 0) {
        flash('Your must enter some text to submit', true);
        return;
    }

    if(countWords($('#textarea1').val()) > parseInt($('#word_limit').val())) {
        flash('Your submission is above the word limit', true);
        return;
    }

    const form = $('#text-upload-form');
    if($('#all-own-work').prop('checked') !== true) {
        flash('You must certify it is all your own work', true);
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
    location.reload();
}