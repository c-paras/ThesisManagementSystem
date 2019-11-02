function uploadFile() {
    makeMultiPartRequest('/submit_file_task', $('#file-upload-form'), (res) => {
        if (res.status === 'fail') {
            flash(res.message, true);
            return;
        }
        flash("Success");
    });
}
