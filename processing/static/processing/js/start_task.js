// Get the CSRF token from cookies.
let cookie = document.cookie
let csrfToken = cookie.substring(cookie.indexOf('=') + 1)

function addTask() {
    // Get input variable.
    var input_command = document.getElementById('input_command').value;

    // Call the run_task_url asynchronously with AJAX.
    $.ajax({
        url: add_task_url,
        type: "POST", // Need a POST type since we pass input data.
        data: { command: input_command },
        dataType: "json",
        headers: {
           'X-CSRFToken': csrfToken
         },
        complete: function(data) {
            pollTasks()
        },
    })
}
