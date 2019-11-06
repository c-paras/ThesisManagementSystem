function updateAllOwnWork() {
    if($('#all-own-work').prop('checked')) {
        $('#all-own-work').val('true');
    } else {
        $('#all-own-work').val('true');
    }
}

function uploadFile(btn) {
    const form = $('#file-upload-form');
    if($('#file-name').val() === '') {
        flash('Please specify a file', true);
        return;
    }
    updateAllOwnWork();
    if($('#all-own-work').prop('checked') !== true) {
        flash('You must certify it is all your own work', true);
        return;
    }
    $(btn).parent().children().each(function(index, value) {
        $(value).toggle();
    });
    makeMultiPartRequest('/submit_file_task', form, (res) => {
        if (res.status === 'fail') {
            $(btn).parent().children().each(function(index, value) {
                $(value).toggle();
            });
            flash(res.message, true);
            return;
        }
        delayToast("Success");
        location.reload();
    });
}

function editFileSubmission() {
    $('#file-upload-form').closest('div.row').show();
}

function cancelFileSubmission() {
    $('#file-upload-form').closest('div.row').hide();
}

$(function() {
    $('#all-own-work').change(updateAllOwnWork());
});
