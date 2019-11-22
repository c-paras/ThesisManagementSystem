
function drawChart() {
  const taskId = (new URLSearchParams(window.location.search)).get('task_id');
  const url = new URL('/task_status', location.href);
  const params = new URLSearchParams([['task_id', taskId]]);

  const urlString = `${url.toString()}?${params.toString()}`;
  makeGETRequest(urlString, (res) => {
    if(res.status === 'fail') {
      flash("Student data request failed, please refresh the page", error=True);
      return;
    }
    const numStudents = res.students.length;
    if (numStudents === 0) {
      flash("No students enrolled", error=True);
      return;
    }
    const marked = ['approved', 'rejected', 'marked', 'cancelled'];
    let markedCount = 0;

    const submitted = ['pending', 'pending mark'];
    let submittedCount = 0;
    for (var i in res.students) {
      if (marked.includes(res.students[i].status.name)) {
        markedCount++;
        continue;
      }
      if (submitted.includes(res.students[i].status.name)) {
        submittedCount++;
        continue;
      }
    }
    const notSubmittedCount = numStudents - (markedCount + submittedCount);
    const data = google.visualization.arrayToDataTable([
      ['Type', '# Students'],
      ['Marked',  markedCount],
      ['Submitted',  submittedCount],
      ['Not Submitted', notSubmittedCount]
    ]);

    const options = {
      height: 'auto',
      backgroundColor: {
        'fillOpacity': 0
      },
      chartArea:{
        width:"100%",
        height: "75%"
      },
      pieHole: 0.4,
      colors: ['#26a69a', '#a66426', '#a6262c']
    };

    const chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(data, options);
  });

}

$(function() {
  if(typeof google !== typeof undefined) {
    google.charts.load('current', {'packages':['corechart']});
    google.charts.setOnLoadCallback(drawChart);
  }
});
