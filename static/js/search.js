console.log('Client side javascript file is loaded')

function searchResults() {
    const form = $('#search-form');
    if (!formValid(form)) {
        return;
    }

    makeRequest('/search', form, (res) => {
        if (res.status === 'fail') {
          flash(res.message, error = true);
        } else {
          
        }
    });
}