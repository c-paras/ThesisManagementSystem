
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
    const marked = {
      names: ['approved', 'rejected', 'marked', 'cancelled'],
      count: 0
    };

    const submitted = {
      names: ['pending', 'pending mark'],
      count: 0
    };

    const partial = {
      names: ['partially marked'],
      count: 0
    };

    for (var i in res.students) {
      const status = res.students[i].status.name;
      if (marked.names.includes(status)) {
        marked.count++;
        continue;
      }
      if (partial.names.includes(status)) {
        partial.count++;
        continue;
      }
      if (submitted.names.includes(status)) {
        submitted.count++;
        continue;
      }
    }
    const notSubmittedCount = numStudents - (marked.count + partial.count + submitted.count);
    const data = google.visualization.arrayToDataTable([
      ['Type', '# Students'],
      ['Not Submitted', notSubmittedCount],
      ['Submitted',  submitted.count],
      ['Partly Marked', partial.count],
      ['Marked',  marked.count],
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
      colors: ['#F25F5C' , '#F8CB65' , '#255957', '#26A69A']
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
