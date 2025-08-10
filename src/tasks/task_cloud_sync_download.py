from tasks.task_dropbox_download import execute as task_dropbox_download
from tasks.task_nexcloud_download import execute as task_nexcloud_download


def execute(context, config):
    task_dropbox_download(context, config)
    task_nexcloud_download(context, config)