function searchResultsPublic() {
  const form = $('#search-form-public');
  if (!formValid(form)) {
    return;
  }
  const searchTerm = $('#search-input-public').val();
  window.location.href = '/search?search=' + searchTerm;

}