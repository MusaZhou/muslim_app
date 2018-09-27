# Create your tasks here
from __future__ import unicode_literals
from celery import shared_task
from management.models import Video, MobileApp
from celery.utils.log import get_task_logger
from django.core.files.storage import default_storage, FileSystemStorage
from django.core.files import File
from celery.result import AsyncResult
import os
from django.conf import settings
from django.db import connection

logger = get_task_logger(__name__)

@shared_task
def test_task():
#     video = Video.objects.get(id=18)
    with open('/home/musa/muslim_app/muslim_app_bk/muslimappbk/media/videos/test.mp4', 'rb') as f:
        file_path = default_storage.save(settings.MEDIA_URL + 'videos/0IQ9T25S4ddd.mp4', f)
        logger.info('finish upload:' + file_path)
        
    with connection.cursor() as cursor:
        cursor.execute("UPDATE management_video SET file=%s WHERE id=%s", ['videos/0IQ9T25S4ddd.mp4', 16])
        
#     Video.objects.raw('update management_video set file=%s where id=%d', ['videos/0IQ9T25S4134.mp4', 19])
#     video_file = default_storage.open('videos/0IQ9T25S4121.mp4')
#     video.file = video_file
#     video.save()

    
@shared_task
def error_handler_task(uuid):
    logger.info('enter error handler, result uuid=' + uuid)
    result = AsyncResult(uuid)
    logger.info('get result')
#     exc = result.get()
    logger.info('Task {0} raised exception: {1!r}'.format(
          uuid, result.traceback))