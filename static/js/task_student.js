function uploadFile(btn) {
    const form = $('#file-upload-form');
    if($('#file-name').val() === '') {
        flash('Please specify a file', true);
        return;
    }
    if($('#all-own-work').prop('checked') !== true) {
        flash('You must certify it is all your own work', true);
        return;
    }
    $(btn).parent().children().each(function(index, value) {
        $(value).toggle();
    });
    makeMultiPartRequest('/submit_file_task', form, (res) => {
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

$(function() {
    $('#all-own-work').change(function() {
        if($('#all-own-work').prop('checked')) {
            $('#all-own-work').val('true');
        } else {
            $('#all-own-work').val('true');
        }
    });
});

function countWords(str) {
    if(str.trim() === ""){
        return 0;
    }
    return str.trim().concat(' ').split(/\s+/).length-1;
}

function updateWordCount(textarea){
    $('#word-counter').html(countWords($(textarea).val()));
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

function openModal(){
    const modal = M.Modal.init($('#text_modal'), {
                                dismissible: false
                               });
    modal[0].open();
    updateWordCount($('#textarea1'));
}

function closeModal(){
    const modal = M.Modal.getInstance($('#text_modal'));
    modal.close();
}