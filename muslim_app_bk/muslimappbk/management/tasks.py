# Create your tasks here
from __future__ import unicode_literals
from celery import shared_task
from .models import Video, Image
from celery.utils.log import get_task_logger
from django.core.files.storage import default_storage
from django.core.files import File
import logging, os, random, string
from django.conf import settings
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist

logger = get_task_logger(__name__)

@shared_task
def upload_file_task(file_name, folder, pk, table_name, file_field_name, random_folder=False):
    logger.info('video_id,file_name:' + str(pk) + ', ' + file_name)
    
    with open(file_name, 'rb') as f:
        base_name = os.path.basename(file_name)
        if random_folder:
            folder =os.path.join(folder, ''.join(random.choices(string.ascii_uppercase + string.digits, k=12)))
        default_storage.save(os.path.join(settings.MEDIA_URL, folder, base_name), f)
    
    with connection.cursor() as cursor:
        cursor.execute("UPDATE " + table_name + " SET " + file_field_name +"=%s WHERE id=%s", [os.path.join(folder, base_name), pk])
        
@shared_task(bind=True)
def update_video_path_task(self, path, task_id, width, height, duration):
    try:
        logger.info('enter update_video_path_task')
        Video.objects.get(upyun_task_id=task_id)
    except ObjectDoesNotExist as exc:
        logger.info('video object has not been created, waiting to retry')
        raise self.retry(exc=exc, countdown=5, max_retries=3)
    else:
        Video.objects.filter(upyun_task_id=task_id).update(file=path, width=width, height=height, duration=duration)
        logger.info('video path updated')
        
@shared_task(bind=True)
def update_image_path_task(self, thumbnail_path, task_id, width, height):
    try:
        logger.info('enter update_image_path_task')
        Image.objects.get(upyun_task_id=task_id)
    except ObjectDoesNotExist as exc:
        logger.info('image object has not been created, waiting to retry')
        raise self.retry(exc=exc, countdown=5, max_retries=3)
    else:
        Image.objects.filter(upyun_task_id=task_id).update(thumbnail_picture=thumbnail_path, width=width, height=height)
        logger.info('video path updated')