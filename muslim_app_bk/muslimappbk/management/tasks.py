# Create your tasks here
from __future__ import unicode_literals
from celery import shared_task
from .models import Video
from celery.utils.log import get_task_logger
from django.core.files.storage import default_storage
from django.core.files import File
import os
from django.conf import settings
from django.db import connection

logger = get_task_logger(__name__)

@shared_task
def upload_video_task(file_name, video_id):
    logger.info('video_id,file_name:' + str(video_id) + ', ' + file_name)
    
    with open(file_name, 'rb') as f:
        base_name = os.path.basename(file_name)
        default_storage.save(settings.MEDIA_URL + 'videos/' + base_name, f)
    
    with connection.cursor() as cursor:
        cursor.execute("UPDATE management_video SET file=%s WHERE id=%s", ['videos/' + base_name, video_id])