# Create your tasks here
from __future__ import unicode_literals
from celery import shared_task
from .models import Video
from celery.utils.log import get_task_logger
from django.core.files.storage import default_storage
from django.core.files import File
import logging, os, random, string
from django.conf import settings
from django.db import connection

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