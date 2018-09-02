from django.db import models
from django.conf import settings
from slugify import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import validators

# Create your models here.
class Profile(models.Model):
    GENDER_CHOICES = (('male', '男'), ('female', '女'))
    name = models.CharField(max_length=50, blank=True)
    gender =models.CharField(max_length=10,
                             choices=GENDER_CHOICES,
                             default='male')
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatar/%Y/%m/%d/",blank=True)
    wechatid = models.CharField(max_length=100,
                                blank=True,
                                db_index=True)
    weiboid = models.CharField(max_length=100,
                               blank=True,
                               db_index=True)
    qqid = models.CharField(max_length=100,
                            blank=True,
                            db_index=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.user_name)
            super(Profile, self).save(*args, **kwargs)

class Image(models.Model):
    #id, content_type, object_id, content_object, url
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    picture = models.ImageField(upload_to="pictures/%Y/%m/%d/",blank=True)

    def __str__(self):
        return self.content_object

class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class AppCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MobileApp(models.Model):
    name = models.CharField(max_length=100,
                            unique=True,
                            db_index=True)
    description = models.TextField()
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video_url = models.URLField(null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(AppCategory, on_delete=models.CASCADE)
    avg_rate = models.DecimalField(max_digits=2,
                                   decimal_places=1,
                                   null=True)
    comment_count = models.PositiveIntegerField(null=True)
    download_count = models.PositiveIntegerField(null=True)
    slug = models.SlugField(unique=True)
    images = GenericRelation(Image, related_query_name='appImages')
    tags = models.ManyToManyField(Tag)

    def slugDefault(self):
        return slugify(self.name)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            super(MobileApp, self).save(*args, **kwargs)

class AppVersion(models.Model):
    APPROVE_CHOICES = (('new', 'new'),
                       ('approved', 'approved'),
                       ('rejected', 'rejected'))
    ACTIVE_CHOICES = (('active', 'active'), ('inactive', 'inactive'))

    version_number = models.CharField(max_length=10,
                                      validators=[validators.RegexValidator("[a-zA-Z0-9\.]*")])
    created_time = models.DateTimeField(auto_now_add=True)
    approve_status = models.CharField(max_length=10,
                                      choices=APPROVE_CHOICES,
                                      default='new')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    null=True, blank=True)
    approved_time = models.DateTimeField(null=True, blank=True)
    mobile_app = models.ForeignKey(MobileApp, on_delete=models.CASCADE, null=True)
    active_status = models.CharField(max_length=10,
                                     choices=ACTIVE_CHOICES,
                                     default='inactive')

    def __str__(self):
        return self.version_number

    def clean(self):
        if self.mobile_app is not None:
            if AppVersion.objects.filter(mobile_app=self.mobile_app, version_number=self.version_number).exists():
                raise ValidationError({'version_number': 'Version number is duplicated on this application.'})

class Evaluation(models.Model):
    APPROVE_CHOICES = (('new', 'new'),
                       ('approved', 'approved'),
                       ('rejected', 'rejected'))

    content = models.TextField()
    rate = models.PositiveSmallIntegerField()
    app = models.ForeignKey(MobileApp, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name='createdEvaluations')
    created_time = models.DateTimeField(auto_now_add=True)
    approve_status = models.CharField(max_length=10,
                                      choices=APPROVE_CHOICES,
                                      default='new')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    related_name='checkedEvaluations',
                                    null=True)

    def __str__(self):
        return self.content

class Comment(models.Model):
    APPROVE_CHOICES = (('new', 'new'),
                       ('approved', 'approved'),
                       ('rejected', 'rejected'))

    content = models.TextField()
    evluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    app = models.ForeignKey(MobileApp, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name='createdComments')
    created_time = models.DateTimeField(auto_now_add=True)
    approve_status = models.CharField(max_length=10,
                                      choices=APPROVE_CHOICES,
                                      default='new')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    related_name='checkedComments',
                                    null=True)

    def __str__(self):
        return self.content

class Download(models.Model):
    download_time = models.DateTimeField(auto_now_add=True)
    os = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100)
    app = models.ForeignKey(MobileApp,
                            on_delete=models.CASCADE,
                            null=True)
