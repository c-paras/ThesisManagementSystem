function flash(msg, error = false) {
  M.Toast.dismissAll();
  const color = (error) ? 'red' : 'blue';
  M.toast({html: msg, classes: `${color} darken-1 rounded`});
}
