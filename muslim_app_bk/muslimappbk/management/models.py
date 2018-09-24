from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_save
from .choices import ACTIVE_CHOICES, APPROVE_CHOICES, GENDER_CHOICES
from django_comments_xtd.moderation import moderator, XtdCommentModerator
from django.urls import reverse
from management.templatetags.custom_tags import verbose_name_filter
from django.db.models.fields import CharField
from star_ratings.models import Rating

# Create your models here.
class Profile(models.Model):
    nick_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nick Name")
    gender =models.CharField(max_length=10, verbose_name="Gender",
                             choices=GENDER_CHOICES, default='male')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Date of birth")
    avatar = models.ImageField(upload_to="avatar/%Y/%m/%d/",blank=True, null=True, verbose_name="Avatar")
    wechatid = models.CharField(max_length=100,blank=True,db_index=True,null=True)
    weiboid = models.CharField(max_length=100,blank=True,db_index=True,null=True)
    qqid = models.CharField(max_length=100,blank=True,db_index=True,null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.user.username)
        super(Profile, self).save(*args, **kwargs)
    
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
        instance.profile.save()

class Image(models.Model):
    #id, content_type, object_id, content_object, url
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    picture = models.ImageField(upload_to="pictures/%Y/%m/%d/",blank=True)
#     test = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.content_object
    
class Video(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    video = models.FileField(upload_to="videos", blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tag')

    def __str__(self):
        return self.name

class AppCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Category')

    def __str__(self):
        return self.name
    
class ActiveAppManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    
class ShownAppManager(ActiveAppManager):
    def get_queryset(self):
        qs_appversion = AppVersion.approved_manager.values_list('mobile_app', flat=True).distinct()
        return super().get_queryset().filter(id__in=qs_appversion)
        

class MobileApp(models.Model):
    name = models.CharField(max_length=100,unique=True,
                            db_index=True, verbose_name='App Name')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    upload_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  verbose_name='Uploader')
#     video_url = models.CharField(max_length=200, blank=True, null=True, verbose_name='Video')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Upload Time')
    category = models.ForeignKey(AppCategory, on_delete=models.CASCADE)
   # avg_rate = models.DecimalField(max_digits=2, default=5.0,
   #                                decimal_places=1,
   #                                null=True, verbose_name='Average Rate')
    comment_count = models.PositiveIntegerField(null=True, verbose_name='Comment Count', default=0)
    download_count = models.PositiveIntegerField(null=True, verbose_name='Download Count', default=0)
    slug = models.SlugField(unique=True, null=True, blank=True)
    images = GenericRelation(Image, related_query_name='imaged_app', verbose_name='Screenshots')
    tags = models.ManyToManyField(Tag, verbose_name='Tags')
    is_active = models.BooleanField(default=False, verbose_name='Active Status')
    icon = models.ImageField(upload_to="icons")
    developer = models.CharField(max_length=100, blank=True, null=True, verbose_name="Developer")
    ratings = GenericRelation(Rating, related_query_name='mobile_apps')
    
    objects = models.Manager()
    active_apps = ActiveAppManager()
    shown_apps = ShownAppManager()

    def slugDefault(self):
        return slugify(self.name)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(MobileApp, self).save(*args, **kwargs)
    
    def latest_version(self):
        if self.canShow():
            return self.appversion_set.filter(approve_status='approved')[0]
        return None
    
    def get_absolute_url(self):
        return reverse('showcase:app', args=[self.slug])
    
    def has_approved_version(self):
        if self.appversion_set.filter(approve_status='approved').count() > 0:
            return True
        return False
    
    def canShow(self):
        return self.is_active and self.has_approved_version()
    
    @property
    def userLink(self):
        return reverse('showcase:app', args=[self.slug])
    
    @property
    def latestAPK(self):
        latestVersion = self.latest_version()
        if latestVersion is not None:
            return self.latest_version().apk.url
        return None
    
    def latestTime(self):
        latestVersion = self.latest_version()
        if latestVersion is not None:
            return latestVersion.created_time
        return None
    
    @property
    def avg_rate(self):
        last_rating = self.ratings.last()
        if last_rating is not None:
            return last_rating.average
        return 5.0
    
class VersionApprovedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(approve_status='approved') 
           
class AppVersion(models.Model):
    version_number = models.CharField(max_length=10,
                                      validators=[validators.RegexValidator("[a-zA-Z0-9\.]*")],
                                      verbose_name='Version No.')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='Created Time')
    approve_status = models.CharField(max_length=10,
                                      choices=APPROVE_CHOICES,
                                      default='new', verbose_name='Approve Status')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    null=True, blank=True, verbose_name='Approved By')
    approved_time = models.DateTimeField(null=True, blank=True, verbose_name='Approved Time')
    mobile_app = models.ForeignKey(MobileApp, on_delete=models.CASCADE, blank=True,
                                   null=True, verbose_name='Application')
    whats_new = models.TextField(blank=True, null=True, verbose_name="What's New")
    apk = models.FileField(upload_to='apk', verbose_name="APK File", validators=[validators.FileExtensionValidator(['apk'])])
    translator = models.CharField(max_length=100, null=True, blank=True, verbose_name="Translator")
    android_version = models.CharField(max_length=100, null=True, blank=True, verbose_name="Supported Android Version")
    
    objects = models.Manager()
    approved_manager = VersionApprovedManager()
    
    def __str__(self):
        return self.version_number

    def clean(self):
        if self.mobile_app is not None:
            if AppVersion.objects.filter(mobile_app=self.mobile_app, version_number=self.version_number).exists():
                raise ValidationError({'version_number': 'Version number is duplicated on this application.'})

class Evaluation(models.Model):
    content = models.TextField(verbose_name='Content')
    rate = models.PositiveSmallIntegerField(verbose_name='Rate')
    app = models.ForeignKey(MobileApp, on_delete=models.CASCADE, verbose_name='Application')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                   related_name='createdEvaluations', verbose_name='Comment By')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='Comment At')
    approve_status = models.CharField(max_length=10,choices=APPROVE_CHOICES,
                                      default='new', verbose_name='Approve Status')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                    related_name='checkedEvaluations',
                                    null=True, verbose_name='Approved By')

    def __str__(self):
        return self.content

class Comment(models.Model):
    content = models.TextField(verbose_name='Content')
    evluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, verbose_name='Evaluation')
    app = models.ForeignKey(MobileApp, on_delete=models.CASCADE, verbose_name='Application')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                   related_name='createdComments', verbose_name='Created By')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    approve_status = models.CharField(max_length=10,choices=APPROVE_CHOICES,
                                      default='new', verbose_name='Approve Status')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,
                                    related_name='checkedComments',
                                    null=True, verbose_name='Approved By')

    def __str__(self):
        return self.content

class Download(models.Model):
    download_time = models.DateTimeField(auto_now_add=True, verbose_name='Download At')
    os = models.CharField(max_length=100, verbose_name='Operating System')
    mobile = models.CharField(max_length=100, verbose_name='Mobile Phone')
    app = models.ForeignKey(MobileApp,on_delete=models.CASCADE,
                            null=True, verbose_name='Application')

class Banner(models.Model):
    title = models.CharField(verbose_name='Title', max_length=100)
    description = models.TextField('Description', blank=True, null=True)
    image = models.ImageField(upload_to='banners', verbose_name='Banner Image')
    link = models.CharField(verbose_name="Link", max_length=200)

class AppCommentModerator(XtdCommentModerator):
    removal_suggestion_notification = True
    email_notification = True

moderator.register(MobileApp, AppCommentModerator)
