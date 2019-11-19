
function drawChart() {
  const taskId = (new URLSearchParams(window.location.search)).get('task_id');
  const url = new URL('/task_status', location.href);
  const params = new URLSearchParams([['task_id', taskId]]);

  const urlString = `${url.toString()}?${params.toString()}`;
  makeGETRequest(urlString, (res) => {
    if(res.status === 'fail') {
      alert("Student data request failed, please refresh the page");
      return;
    }
    const numStudents = res.students.length;
    const marked = ['approved', 'rejected', 'marked', 'cancelled'];
    let markedCount = 0;

    const submitted = ['pending', 'pending_mark'];
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
        height: "90%"
      },
      pieHole: 0.4,
      colors: ['#a66426', '#a6262c', '#26a69a']
    };

    const chart = new google.visualization.PieChart(document.getElementById('piechart'));

    chart.draw(data, options);
  });

}

$(function() {
  google.charts.load('current', {'packages':['corechart']});
  google.charts.setOnLoadCallback(drawChart);
});
