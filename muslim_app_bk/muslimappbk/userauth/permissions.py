from management.models import MobileApp
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(MobileApp)
permission = Permission.objects.create(
    codename='can_approve_app',
    name='Can Approve Applications',
    content_type=content_type,
)