function uploadFile(btn) {
    const form = $('#file-upload-form');
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
