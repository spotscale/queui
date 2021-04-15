from django.shortcuts import render
from django.urls import reverse
from .models import ProcessingTask, ProcessingStatus
from django.http import HttpResponse, JsonResponse
from django.core.serializers import serialize

import json
import subprocess
import threading

# I imagine we want a call_task() function and an on_task_finished() function here.
# The latter would move the task from the database to a separate "finished" database, call the next task
# and update all the queue positions in the database.
# An alternative would be to call python function asynchronously on server start that performs the cmd call at
# the top of the queue, then goes on with the next task, updating queue positions.
# If no task exists, the process might wait a few seconds and then poll the database again.


def check_next_task():
    print("Checking next task")

    tasks = ProcessingTask.objects.filter(is_done=False).order_by('position')

    if tasks:
        task = tasks.first()

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
        print("Task " + task.id + " failed.")
        print(task.call)
        print(e)
    task.is_done = True
    task.save()
    print("Finished task " + str(task.position))

    # Remove from status.
    status = ProcessingStatus.objects.get()
    status.current_task = None
    status.save()

    if status.is_running:
        check_next_task()


def add_task(request):
    # Get last position index in queue.
    tasks = ProcessingTask.objects.order_by('-position')
    current_queue_length = tasks.first().position
    # print(json.loads(request.body))

    # Create new task.
    task = ProcessingTask()
    task.title = "Just another task"
    task.added_by = "Mikael"
    task.position = current_queue_length + 1
    # task.call = "python C:/utveckling/Django/queue_gui/print_tet.py TaskID:" + str(task.position)
    task.call = request.POST['command']
    task.save()

    status = ProcessingStatus.objects.get()
    if status.is_running:
        check_next_task()

    return HttpResponse(str(task.position))  # TODO THis should probably be a JsonResponse later


def get_current_task(request):
    # Get current task from database.
    current_task = ProcessingStatus.objects.get().current_task

    if not current_task:
        # Create an empty json element.
        current_task_json = serialize("json", [])
        print("current empty task")
    else:
        # Serialize the task object as json.
        current_task_json = serialize("json", [current_task])
        print("current task: " + str(current_task.pk))

    return HttpResponse(current_task_json, content_type="application/json")


def get_finished_tasks(request):
    # Get all finished tasks from database.
    finished_tasks = ProcessingTask.objects.filter(is_done=True).order_by('-position')

    # Serialize the task objects as json.
    finished_tasks_json = serialize("json", finished_tasks)

    # Pass them as an HttpResponse (JsonResponse would try to serialize the variable again).
    return HttpResponse(finished_tasks_json, content_type="application/json")


def get_queued_tasks(request):
    # Get all queued (non-finished) tasks from database.
    finished_tasks = ProcessingTask.objects.filter(is_done=False)

    # Serialize the task objects as json.
    queued_tasks_json = serialize("json", finished_tasks)

    # Pass them as an HttpResponse (JsonResponse would try to serialize the variable again).
    return HttpResponse(queued_tasks_json, content_type="application/json")


def index(request):
    print("Entering index function")
    task_list = ProcessingTask.objects.all()
    log_folder = "C:/utveckling/Django/queue_gui_processing"

    # Check if a ProcessingStatus exists and create one if not.
    status = ProcessingStatus.objects.all()
    if not status:
        new_status = ProcessingStatus()
        new_status.is_running = True
        new_status.current_task = None
        new_status.save()

    default_command = "python C:/utveckling/Django/queue_gui/print_tet.py whatevs"

    return render(request, 'processing/index.html', {'start_text': default_command})
