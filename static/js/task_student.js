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
        delayToast("Success");
        location.reload();
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
