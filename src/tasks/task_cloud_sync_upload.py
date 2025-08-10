from tasks.task_dropbox_upload import execute as task_dropbox_upload
from tasks.task_nexcloud_upload import execute as task_nexcloud_upload


def execute(context, config):
    task_dropbox_upload(context, config)
    task_nexcloud_upload(context, config)