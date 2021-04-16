from django.db import models
from django.utils import timezone


class ProcessingTask(models.Model):
    # Title of the task.
    title = models.CharField(default="Task", max_length=200)

    # Name of person who added the task.
    added_by = models.CharField(max_length=200)

    # Position in queue. No default value as this depends on queue length.
    # position = models.PositiveIntegerField(unique=True)
    # TODO Maybe the queue should be an own table, with ProcessingTasks as foreign keys.

    # Whether task is done.
    is_done = models.BooleanField(default=False)

    # The command line call.
    call = models.CharField(max_length=8191)  # Max length chosen from Windows cmd max call length.

    # Timestamp of task creation.
    created_date = models.DateTimeField(auto_now_add=True)

    # Timestamp of task completion.
    completed_date = models.DateTimeField(null=True)

    # TODO Field(s) for whether the task was aborted, crashed or successful?

    def __str__(self):
        message = str(self.title) + ", id " + str(self.pk) + ", created " + str(self.created_date)
        return message


class ProcessingStatus(models.Model):
    # Server status: running or paused.
    is_running = models.BooleanField(default=False)

    # The task that is currently being processed.
    current_task = models.ForeignKey(ProcessingTask, null=True, on_delete=models.SET_NULL)


class QueuePosition(models.Model):
    # Position in queue.
    position = models.PositiveIntegerField(unique=True)

    # Foreign key to a task.
    task = models.ForeignKey(ProcessingTask, null=False, on_delete=models.CASCADE)
    # TODO Ideally we would want all consecutive queuepositions to decrement their position by one on delete.

    # TODO Use class Meta and ordering to order this table on position.
