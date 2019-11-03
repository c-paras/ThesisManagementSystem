function uploadFile() {
    if($('#all-own-work').prop('checked') !== true) {
        flash('You must certify it is all your own work', true);
        return;
    }
    makeMultiPartRequest('/submit_file_task', $('#file-upload-form'), (res) => {
        if (res.status === 'fail') {
            flash(res.message, true);
            return;
        }
        flash("Success");
    });
}
