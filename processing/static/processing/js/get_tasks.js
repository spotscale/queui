
function pollTasks() {
    $.ajax({
        url: get_current_url,
        type: "GET",
        success: function(data) {
            fillTaskList(data, "currentTask")
        },
    })

    $.ajax({
        url: get_queued_url,
        type: "GET",
        success: function(data) {
            fillTaskList(data, "queuedTasks")
        },
    })

    $.ajax({
        url: get_finished_url,
        type: "GET",
        success: function(data) {
            fillTaskList(data, "finishedTasks")
        },
    })
}

// Naive check if data has updated.
// TODO This is not working as intended as it alternates between queued and finished tasks.
var previousData = null
function checkTasksChanged(data) {
    if (data != previousData) {
        previousData = data
        return true
    }
    else {
        return false
    }
}

function fillTaskList(data, listToPopulate) {
    // TODO Check if data has changed since last time this list was populated (to avoid re-rendering so much).

    document.getElementById(listToPopulate).innerHTML = ""

    if (data != "")
    {
        for (var i = 0; i < data.length; i++) {
            var task = data[i]
            var title = task["fields"]["title"]
            var addedBy = task["fields"]["added_by"]
            var position = task["fields"]["position"]
            var is_done = task["fields"]["is_done"]
            var call = task["fields"]["call"]

            var node = document.createElement('div') // Maybe there's a better type than div for this one...
            node.className = "processingTask"
            var titleNode = document.createElement('div')
            titleNode.className = "taskTitle"
            titleNode.innerText = title
            var callNode = document.createElement('div')
            callNode.className = "taskCall"
            callNode.innerText = call
            var addedByNode = document.createElement('div')
            addedByNode.className = "taskAddedBy"
            addedByNode.innerText = addedBy
            node.appendChild(titleNode)
            node.appendChild(callNode)
            node.appendChild(addedByNode)
            document.getElementById(listToPopulate).appendChild(node)
        }
    }
}

// Start the polling of tasks with a millisecond interval.
var threadInterval = setInterval(pollTasks, 5000)
