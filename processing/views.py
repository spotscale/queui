from django.shortcuts import render
from django.urls import reverse
from .models import ProcessingTask, ProcessingStatus, QueuePosition
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie

import json
import subprocess
import threading


def check_next_task():
    """Checks if server is running and nothing is currently being processed, then starts the next task in queue."""
    print("Checking next task")

    status = ProcessingStatus.objects.first()
    ready_for_task = False
    if status:
        ready_for_task = (status.is_running and not status.current_task)
    else:
        print("Warning: No status object found.")

    if ready_for_task:
        queue = QueuePosition.objects.all().order_by('position')

        if queue:
            task = queue.first().task

            # Start the task.
            thread = threading.Thread(target=run_task, args=[task], daemon=True)
            thread.start()

            # Set it to the currently running task.
            status = ProcessingStatus.objects.get()
            status.current_task = task
            status.save()
        else:
            print("No tasks available")


def start_processing():
    print("Starting processing")
    status = ProcessingStatus.objects.get()
    status.is_running = True
    status.save()

    # Start next task in processing queue.
    check_next_task()


def pause_processing():
    print("Pausing processing")
    status = ProcessingStatus.objects.get()
    status.is_running = False
    status.save()


def switch_processing(request):
    status = ProcessingStatus.objects.get()
    if status.is_running:
        pause_processing()
    else:
        start_processing()

    # Get status again as it has probably changed.
    status = ProcessingStatus.objects.get()
    return HttpResponse(status.is_running)


def check_processing(request):
    """Just return whether server is running or not."""
    status = ProcessingStatus.objects.get()

    return HttpResponse(status.is_running)


def run_task(task):
    print("Running a task!!")
    try:
        subprocess.check_call(task.call)
    except Exception as e:
        print("Task " + str(task.id) + " failed.")
        print(task.call)
        print(e)
    task.is_done = True
    task.save()
    print("Finished task " + str(task.id))

    # Remove this task from queue and update all other positions.
    try:
        with transaction.atomic():  # Don't allow any other changes to database while the following runs.
            queue = QueuePosition.objects.all().order_by('position')
            if queue:
                if queue[0].task != task:
                    print("Warning: First item in queue was not the same as the completed task. Something is wrong!")
                else:
                    for idx, queue_item in enumerate(queue):
                        if idx == 0:
                            queue_item.delete()
                        else:
                            queue_item.position = idx - 1
                            queue_item.save()
    except Exception as e:  # TODO Catch more specific exceptions.
        print("Something failed when updating queue.")
        print(e)
        # TODO Maybe we want to clear the queue or something.

    # Remove from status.
    status = ProcessingStatus.objects.get()
    status.current_task = None
    status.save()

    check_next_task()


# @ensure_csrf_cookie
def add_task(request):
    # Get length of queue.
    current_queue_length = len(QueuePosition.objects.all())

    # Create new task.
    task = ProcessingTask()
    task.title = "Just another task"
    task.added_by = "Mikael"
    task.position = current_queue_length + 1
    task.call = request.POST['command']
    task.save()

    # Create queue position.
    queue_pos = QueuePosition()
    queue_pos.position = current_queue_length
    queue_pos.task = task
    queue_pos.save()

    check_next_task()

    return HttpResponse(str(task.position))  # TODO THis should probably be a JsonResponse later


def get_current_task(request):
    # Get current task from database.
    status = ProcessingStatus.objects.first()

    if status:
        current_task = status.current_task
    else:
        current_task = None

    if not current_task:
        # Create an empty json element.
        current_task_json = serialize("json", [])
    else:
        # Serialize the task object as json.
        current_task_json = serialize("json", [current_task])

    return HttpResponse(current_task_json, content_type="application/json")


def get_finished_tasks(request):
    # Get all finished tasks from database.
    finished_tasks = ProcessingTask.objects.filter(is_done=True)

    # Serialize the task objects as json.
    finished_tasks_json = serialize("json", finished_tasks)

    # Pass them as an HttpResponse (JsonResponse would try to serialize the variable again).
    return HttpResponse(finished_tasks_json, content_type="application/json")


def get_queued_tasks(request):
    # Get whole queue.
    queue = QueuePosition.objects.all()
    # Get all ProcessingTasks that appear as foreign keys in queue and that is not a foreign key in ProcessingStatus.
    queued_tasks = ProcessingTask.objects.filter(queueposition__in=queue, processingstatus=None)

    # Serialize the task objects as json.
    queued_tasks_json = "{}"
    if queued_tasks:
        queued_tasks_json = serialize("json", queued_tasks)

    # Pass them as an HttpResponse (JsonResponse would try to serialize the variable again).
    return HttpResponse(queued_tasks_json, content_type="application/json")


@ensure_csrf_cookie
def index(request):
    print("Entering index function")
    task_list = ProcessingTask.objects.all()

    # Check if a ProcessingStatus exists and create one if not.
    status = ProcessingStatus.objects.all()
    if not status:
        new_status = ProcessingStatus()
        new_status.is_running = True
        new_status.current_task = None
        new_status.save()

    default_command = "python C:/spotscale/development/queui/wait_and_print.py whatevs"

    return render(request, 'processing/index.html', {'start_text': default_command})
