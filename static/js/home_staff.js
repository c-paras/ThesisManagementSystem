function toggleViewAssessor() {
    if($('#reject-check').prop('checked') === true) {
        $('#assessor-view').hide();
    } else {
        $('#assessor-view').show();
    }
}

function openRequestModal(studentId, topicId) {
    const data = {
        'student_id': studentId,
        'topic_id': topicId
    };

    makeRequestCustomData('/lookup_request', data, (res) => {
        if(res.status === 'fail') {
            flash(res.message, error = true);
            return;
        }
        if(res.reqStatus !== 'pending') {
            flash("Topic unavailable to accept or reject");
            return;
        }
        const form = $('#respond-form');
        form.children('input[name=topic]').val(topicId);
        form.children('input[name=student-id]').val(studentId);
        $('#accept-check').prop('checked', true);
        $('#reject-check').prop('checked', false);
        $('#student-name').text(res.userName);
        $('#topic-name').text(res.topicName);

        const d = new Date(res.reqDate);
        $('#date-requested').text(d.toLocaleDateString() + ' at ' + d.toLocaleTimeString());
        toggleViewAssessor();
        const modal = M.Modal.getInstance($('#request-modal'));
        modal.open();
    });
}

function submitRequest() {
    const form = $('#respond-form');
    const assessor = form.find('select[name=assessor]');
    if($('#accept-check').prop('checked') && assessor.val() === null) {
        flash('Must select assessor', true);
        return;
    }
    makeRequest('/respond_request', form, (res) => {
        if(res.status === 'fail') {
            flash(res.message, error = true);
            return;
        }
        delayToast('Response sent');
        location.reload();
    });
}

$(function() {
    // Initialise materalize style select statements
    $('select').formSelect();
    $('#reject-check').change(function() {
        toggleViewAssessor();
    });
    $('#accept-check').change(function() {
        toggleViewAssessor();
    });

    // Fix the select assessor box in the modal
    // https://github.com/Dogfalo/materialize/issues/1385
    M.FormSelect.init($('#assessor-select'), {dropdownOptions:{container:document.body}});
});
