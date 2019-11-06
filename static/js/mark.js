function updateMarks(taskId, studentid, taskCriteriaId) {
    let marks = [];

    $("[id='enteredMark']").each((function() {
        marks.push($(this).val());
      }));

    let feedback = [];
    $("[id='enteredFeedback']").each((function() {
        feedback.push($(this).val());
      }));
    
    let data = {
    'marks': marks,
    'feedback': feedback,
    'taskId': taskId,
    "studentId": studentid,
    "taskCriteria": taskCriteriaId
    };

    makePOSTRequest('/mark', data, (res) => {
      if (res.status === 'fail') {
          flash(res.message, error = true);
      } else {
          console.log(res.status);
      }
    });
}